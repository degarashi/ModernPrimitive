import math
from collections.abc import Iterable, Sequence
from typing import ClassVar, cast

import bpy
import numpy as np
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Context, Event, Object, Operator
from mathutils import Matrix, Quaternion, Vector, geometry

from ..aux_func import calc_aabb, get_evaluated_vertices, is_primitive_mod, mul_vert_mat
from ..aux_math import is_uniform
from ..aux_other import classproperty
from ..constants import MODERN_PRIMITIVE_PREFIX


class BBox:
    def __init__(self, vert: Iterable[Vector]):
        (self.min, self.max) = calc_aabb(vert)
        self.size = self.max - self.min
        self.center = (self.min + self.max) / 2

    def __str__(self) -> str:
        return f"BBox(min={self.min}, max={self.max},\
size={self.size}, center={self.center})"


def _auto_axis(pts: Iterable[Iterable[float]]) -> tuple[Vector, Vector, Vector]:
    # Converts the vertex coordinates to NumPy array
    pts_np = np.array(pts)
    # Data standardization
    mean_coords = pts_np.mean(axis=0)
    pts_np = pts_np - mean_coords
    # calc Convariance matrix
    cov = np.cov(pts_np, rowvar=False)

    # Eigen values and Eigen vectors
    eigval, eigvec = np.linalg.eigh(cov)
    # Sorting the unique vec in descending order
    eigvec = eigvec[:, eigval.argsort()[::-1]]

    a0 = Vector(eigvec[:, 0])
    a1 = Vector(eigvec[:, 1])
    a2 = Vector(eigvec[:, 2])
    return a0, a1, a2


def to_4d_0(vec: Vector) -> Vector:
    ret = vec.to_4d()
    ret[3] = 0
    return ret


class ConvertTo_BaseOperator(Operator):
    @classproperty
    def type_name(cls):
        return cls.type.name

    @classmethod
    def get_bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_convert_to_{cls.type_name.lower()}"

    @classmethod
    def get_bl_label(cls):
        return f"Convert object to Modern{cls.type_name}"

    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}
    keep_original: BoolProperty(name="Keep Original", default=False)
    apply_scale: BoolProperty(name="Apply Scaling", default=True)

    # The main axis of Height (the Width axis is the other)
    main_axis: EnumProperty(
        name="Base Axis",
        default="Auto",
        items=(
            ("Auto", "Auto", ""),
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
        ),
    )
    invert_main_axis: BoolProperty(name="Invert", default=False)
    treat_as_short: BoolProperty(name="Treat As Short", default=True)
    postfix: StringProperty(name="postfix", default="_converted")
    copy_modifier: BoolProperty(name="Copy Modifiers", default=True)
    copy_material: BoolProperty(name="Copy Material", default=True)

    def draw(self, context: Context) -> None:
        layout = self.layout

        layout.prop(self, "keep_original")
        layout.prop(self, "apply_scale")
        box = layout.box()
        box.prop(self, "main_axis")
        if self.main_axis == "Auto":
            box.prop(self, "treat_as_short")
        box.prop(self, "invert_main_axis")
        layout.prop(self, "postfix")

        box = layout.box()
        box.prop(self, "copy_modifier")
        box.prop(self, "copy_material")

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        context = cast(Context, context)

        sel = context.selected_objects
        if len(sel) == 0:
            return False
        for obj in sel:
            if obj is None or obj.type != "MESH":
                return False
        return True

    def _handle_proc(
        self, context: Context, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        raise NotImplementedError("This method should be implemented by subclass")

    def _handle_obj(self, context: Context, obj: Object, err_typ: str) -> None:
        # Acquiring all the vertices of the object,
        #   it may be heavy, so there is room for improvement.
        verts = get_evaluated_vertices(context, obj)

        # If the number of vertices is less than 2, conversion is not possible.
        if len(verts) < 2:
            self._report_error(err_typ, obj, "it's number of vertices is less than 2")
            return

        # Quotanion for rotating the main axis to the Z axis
        pre_rot: Quaternion
        should_flip: bool = False
        # _handle Proc method handles the Z axis as height,
        #   so convert it in a timely manner.
        match self.main_axis:
            case "Auto":
                # If the axis mode is Auto,
                #   an error will be made if the scale value is not uniform
                #        at this time.
                if not is_uniform(obj.scale):
                    self._report_error(
                        err_typ,
                        obj,
                        "it didn't have a uniform scaling value.\n"
                        "Try set axis manually.",  # noqa: E501
                    )
                    return
                axis = _auto_axis(verts)
                m = Matrix(
                    (
                        to_4d_0(axis[2]),
                        to_4d_0(axis[1]),
                        to_4d_0(axis[0]),
                        (0, 0, 0, 1),
                    )
                )
                rot = m.to_quaternion()
                # The generated coordinate axes here may not be optimal
                #   (except for the Z axis)
                # treat Z-axis to the main axis and projected to 2D
                z_axis = axis[0]
                verts_xy = mul_vert_mat(verts, rot.to_matrix())
                verts_xy = [v.xy for v in verts_xy]

                # calc 2D convex
                convex_hull_idx = geometry.convex_hull_2d(verts_xy)
                verts_2d = [verts_xy[convex_hull_idx[0]]]
                prev_pos = verts_2d[0]
                for idx in convex_hull_idx[1:]:
                    pos = verts_xy[idx]
                    # Omit the vertices of almost the same position
                    if (prev_pos - pos).length_squared < 1e-12:
                        continue
                    prev_pos = pos
                    verts_2d.append(pos)

                if len(verts_2d) < 2:
                    self._report_error(
                        err_typ,
                        obj,
                        "error occurred by calculation when determining the conversion axis automatically",  # noqa: E501
                    )
                    return

                mat_rot90 = Matrix.Rotation(math.radians(90), 3, Vector((0, 0, 1)))
                best_normal: Vector
                best_dist: float = 1e24  # some Big number
                for i in range(len(verts_2d)):
                    v0, v1 = verts_2d[i], verts_2d[(i + 1) % len(verts_2d)]
                    # normal vector from edge vertices
                    normal = mat_rot90 @ ((v1 - v0).normalized().to_3d())

                    maxv = -1e24  # some Small number
                    for v in verts_2d:
                        maxv = max((v - v0).dot(normal), maxv)
                    if best_dist > maxv:
                        best_dist = maxv
                        best_normal = normal

                # best_normal is a temporary coordinate system above,
                #   so return it to the object coordinate system.
                invrot_mat = rot.inverted().to_matrix()
                best_normal = invrot_mat @ best_normal

                # Treat as the Y-axis
                y_axis = best_normal
                # X-axis is found by taking the cross product of y_axis and z_axis
                x_axis = y_axis.cross(z_axis)

                # If there is a flag to handle the short side as an Z axis
                #   replace the axis here.
                if self.treat_as_short:
                    z_axis, y_axis = y_axis, z_axis
                    # flip X-axis
                    x_axis *= -1

                m = Matrix(
                    (
                        to_4d_0(x_axis),
                        to_4d_0(y_axis),
                        to_4d_0(z_axis),
                        (0, 0, 0, 1),
                    )
                )
                pre_rot = m.to_quaternion()
                # If the Z axis is facing down in the object coordinate system,
                #   flip automatically
                if (pre_rot @ Vector((0, 0, 1))).z < 0:
                    should_flip = True

            case "X":
                # -90 degrees rotation around the Y axis
                pre_rot = Quaternion(((0, 1, 0)), math.radians(-90))
            case "Y":
                # 90 degrees around the X-axis
                pre_rot = Quaternion((1, 0, 0), math.radians(90))
            case "Z":
                # Do nothing
                pre_rot = Quaternion()
        # invert axis if flag set
        if self.invert_main_axis:
            should_flip = not should_flip

        if should_flip:
            pre_rot.rotate(Quaternion((0, 1, 0), math.radians(180)))
        mat_rot90 = pre_rot.to_matrix()

        # get bound_box info (size, average)
        # Bounding box when the z-axis is the main axis
        verts = mul_vert_mat(verts, mat_rot90)
        bbox = BBox(verts)
        new_obj, offset = self._handle_proc(context, bbox, verts)
        new_obj.name = obj.name + self.postfix

        new_obj.matrix_world = (
            obj.matrix_world
            @ pre_rot.inverted().to_matrix().to_4x4()
            @ Matrix.Translation(bbox.center)
            @ Matrix.Translation(offset)
        )

        # copy materials
        if self.copy_material:
            if obj.data.materials:
                new_obj.data.materials.clear()
                for m in obj.data.materials:
                    new_obj.data.materials.append(m)

        # copy modifiers
        if self.copy_modifier:
            for m_src in obj.modifiers:
                if is_primitive_mod(m_src):
                    continue

                m_dst = new_obj.modifiers.new(m_src.name, m_src.type)

                # collect names of writable properties
                props = [
                    p.identifier for p in m_src.bl_rna.properties if not p.is_readonly
                ]

                # copy properties
                for prop in props:
                    setattr(m_dst, prop, getattr(m_src, prop))

        if self.apply_scale:
            bpy.ops.object.mpr_apply_scale(strict=False)

        if not self.keep_original:
            bpy.data.objects.remove(obj)

    def _report_error(self, err_typ: str, obj: Object, msg: str) -> None:
        self.report({err_typ}, f'Couldn\'t convert "{obj.name}" because {msg}')

    def invoke(self, context: Context, event: Event) -> set[str]:
        self.keep_original = event.shift
        return self.execute(context)

    def execute(self, context: Context | None) -> set[str]:
        sel = context.selected_objects.copy()

        # If there is only one target object, treat it as an error
        err_typ = "WARNING" if len(sel) > 1 else "ERROR"
        # Copy the list because the object may be deleted in the loop
        for obj in sel.copy():
            self._handle_obj(context, obj, err_typ)

        return {"FINISHED"}

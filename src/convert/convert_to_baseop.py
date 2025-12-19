import math
from collections.abc import Iterable, Sequence
from typing import ClassVar, cast

import bmesh
import bpy
import numpy as np
from bmesh.types import BMesh
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Context, Event, Object, Operator
from mathutils import Matrix, Quaternion, Vector, geometry

from ..util.aux_node import copy_geometry_node_params
from ..util.aux_func import get_evaluated_obj, is_primitive_mod, mul_vert_mat
from ..util.aux_math import BBox, is_uniform
from ..util.aux_other import classproperty, get_bmesh
from ..constants import MODERN_PRIMITIVE_PREFIX
from ..exception import DGException
from .common_func import calc_fittest_axis
from .common_type import IndexConvOPT


def vector_conv(source: Vector, index_conv: IndexConvOPT = None) -> Vector:
    if index_conv is None:
        return source.copy()
    return Vector(source[index_conv[i]] for i in range(3))


def index_to_mat(index_conv: IndexConvOPT) -> Matrix:
    if index_conv is None:
        index_conv = (0, 1, 2)

    COLUMN_N = 3
    row0 = tuple(1 if index_conv[0] == i else 0 for i in range(COLUMN_N))
    row1 = tuple(1 if index_conv[1] == i else 0 for i in range(COLUMN_N))
    row2 = tuple(1 if index_conv[2] == i else 0 for i in range(COLUMN_N))
    return Matrix((row0, row1, row2))


class CantConvertException(DGException):
    def __init__(self, reason: str):
        super().__init__(reason)


def calc_volume(bm: BMesh) -> float:
    volume: float = 0.0
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for face in bm.faces:
        v0, v1, v2 = (v.co for v in face.verts)
        volume += v0.dot(v1.cross(v2)) / 6.0

    return abs(volume)


def _auto_axis(pts: Iterable[Iterable[float]]) -> tuple[Vector, Vector, Vector]:
    # Converts the vertex coordinates to NumPy array
    pts_np = np.array(pts)
    # Data standardization
    mean_coords = pts_np.mean(axis=0)
    pts_np = pts_np - mean_coords
    # calc Covariance matrix
    cov = np.cov(pts_np, rowvar=False)

    # Eigen values and Eigen vectors
    eigval, eigvec = np.linalg.eigh(cov)
    # Sorting the eigenvectors in descending orde
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
    postfix: StringProperty(name="postfix", default="_converted")
    copy_modifier: BoolProperty(name="Copy Modifiers", default=True)
    copy_material: BoolProperty(name="Copy Material", default=True)

    def draw(self, context: Context) -> None:
        layout = self.layout

        layout.prop(self, "keep_original")
        layout.prop(self, "apply_scale")
        box = layout.box()
        box.prop(self, "main_axis")
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
        return all(
            not (obj is None or obj.mode != "OBJECT" or obj.type != "MESH") for obj in sel
        )

    def _handle_proc(self, context: Context, verts: Sequence[Vector]) -> tuple[Object, Vector]:
        raise NotImplementedError("This method should be implemented by subclass")

    def _handle_auto_axis(
        self,
        verts: Sequence[Vector],
        obj: Object,
        bm: BMesh,
    ) -> tuple[Quaternion, bool]:
        pre_rot: Quaternion
        should_flip: bool = False

        # If the axis mode is Auto,
        #   an error will be made if the scale value is not uniform
        #        at this time.
        if not is_uniform(obj.scale):
            raise CantConvertException(
                "it didn't have a uniform scaling value.\nTry set axis manually."
            )

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

        MIN_LENGTH_SQ = 1e-12
        # calc 2D convex
        convex_hull_idx = geometry.convex_hull_2d(verts_xy)
        verts_2d = [verts_xy[convex_hull_idx[0]]]
        prev_pos = verts_2d[0]
        for idx in convex_hull_idx[1:]:
            pos = verts_xy[idx]
            # Omit the vertices of almost the same position
            if (prev_pos - pos).length_squared < MIN_LENGTH_SQ:
                continue
            prev_pos = pos
            verts_2d.append(pos)

        MIN_VERTS_2D = 2
        if len(verts_2d) < MIN_VERTS_2D:
            raise CantConvertException(
                "error occurred by calculation when determining the conversion axis automatically"  # noqa: E501
            )

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
        x_axis: Vector = y_axis.cross(z_axis)

        # <z, x, y at this point in order of longest>

        # Convert once with the z-axis as the longest (no offset adjustment)
        m = Matrix(
            (
                to_4d_0(x_axis),
                to_4d_0(y_axis),
                to_4d_0(z_axis),
                (0, 0, 0, 1),
            )
        )
        verts2 = mul_vert_mat(verts, m)
        axis_idx = calc_fittest_axis(self.SizeType, BBox(verts2), verts2, calc_volume(bm))
        axis3 = (x_axis, y_axis, z_axis)
        new_axis = tuple(axis3[idx] for idx in axis_idx)

        m = Matrix(
            (
                to_4d_0(new_axis[0]),
                to_4d_0(new_axis[1]),
                to_4d_0(new_axis[2]),
                (0, 0, 0, 1),
            )
        )
        pre_rot = m.to_quaternion()
        # If the Z axis is facing down in the object coordinate system,
        #   flip automatically
        if (pre_rot @ Vector((0, 0, 1))).z < 0:
            should_flip = True
        return (pre_rot, should_flip)

    def _make_primitive(
        self, verts: Sequence[Vector], pre_rot: Quaternion, context: Context, obj: Object
    ) -> Object:
        verts = mul_vert_mat(verts, pre_rot.to_matrix())
        bbox = BBox(verts)
        new_obj, offset = self._handle_proc(context, bbox, verts)
        new_obj.name = obj.name + self.postfix

        new_obj.matrix_world = (
            obj.matrix_world
            @ pre_rot.inverted().to_matrix().to_4x4()
            @ Matrix.Translation(bbox.center)
            @ Matrix.Translation(offset)
        )
        return new_obj

    def _make_axis_and_primitive(self, context: Context, obj: Object) -> Object:
        # Acquiring all the vertices of the object,
        #   it may be heavy, so there is room for improvement.
        eval_obj = get_evaluated_obj(context, obj)
        with get_bmesh(eval_obj, False, False, False) as bm:
            verts = [v.co for v in bm.verts]

            # If the number of vertices is less than 2, conversion is not possible.
            MIN_VERTS = 2
            if len(verts) < MIN_VERTS:
                raise CantConvertException("it's number of vertices is less than 2")

            # Quaternion for rotating the main axis to the Z axis
            pre_rot: Quaternion
            should_flip: bool = False
            # _handle Proc method handles the Z axis as height,
            #   so convert it in a timely manner.
            match self.main_axis:
                case "Auto":
                    pre_rot, should_flip = self._handle_auto_axis(verts, obj, bm)
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

            # get bound_box info (size, average)
            # Bounding box when the z-axis is the main axis
            return self._make_primitive(verts, pre_rot, context, obj)

    def _handle_obj(self, context: Context, obj: Object, err_typ: str) -> None:
        try:
            # Create primitive based on obj
            new_obj = self._make_axis_and_primitive(context, obj)
        except CantConvertException as e:
            self._report_error(err_typ, obj, str(e))
            return

        if self.keep_original:
            # Temporarily set newly created object as active,
            # so subsequent operations (copying materials,
            # copying modifiers, applying scale) can be executed correctly
            with context.temp_override(
                active_object=new_obj, object=new_obj, selected_objects=[new_obj]
            ):
                # copy materials
                if self.copy_material and obj.data.materials:
                    new_obj.data.materials.clear()
                    for m in obj.data.materials:
                        new_obj.data.materials.append(m)

                # copy modifiers (except mpr-modifier)
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
        else:
            # Copy new_obj contents (mesh, modifier, material, scale, position, rotation) into obj
            tmp_objdata = obj.data
            obj.data = new_obj.data
            bpy.data.meshes.remove(tmp_objdata)

            # make obj selected
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # MPR base assets have no Material settings, so do not copy materials

            # MPR base assets have only one MPR modifier, so copy that
            for m_src in new_obj.modifiers:
                if is_primitive_mod(m_src):
                    m_dst = obj.modifiers.new(m_src.name, m_src.type)
                    m_dst.node_group = m_src.node_group
                    copy_geometry_node_params(m_dst, m_src)

            obj.location = new_obj.location
            obj.rotation_euler = new_obj.rotation_euler
            obj.scale = new_obj.scale

            # Delete temporary object after use
            bpy.data.objects.remove(new_obj)

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

from bpy.types import Operator, Context, Object
from ..constants import MODERN_PRIMITIVE_PREFIX
from typing import cast, Iterable
from bpy.props import BoolProperty, EnumProperty
import bpy
from ..aux_func import (
    is_modern_primitive,
    get_bound_box,
    get_evaluated_vertices,
    mul_vert_mat,
)
from mathutils import Matrix, Vector, Quaternion
import math
import numpy as np
from ..aux_math import is_uniform


class BBox:
    def __init__(self, vert: Iterable[Vector]):
        (self.min, self.max) = get_bound_box(vert)
        self.size = self.max - self.min
        self.center = (self.min + self.max) / 2

    def __str__(self) -> str:
        return f"BBox(min={self.min}, max={self.max},\
size={self.size}, center={self.center})"


def _auto_axis(data: Iterable[Iterable[float]]) -> Quaternion:
    verts = np.array(data)
    # Data standardization
    verts2 = verts - verts.mean(axis=0) / np.std(verts, axis=0)
    # calc Convariance matrix
    cov = np.cov(verts2, rowvar=False)
    # Eigen values and Eigen vectors
    eigval, eigvec = np.linalg.eig(cov)
    # Sorting the unique value in descending order
    sort_idx = np.argsort(eigval)[::-1]
    eigval = eigval[sort_idx]
    eigvec = eigvec[:, sort_idx]

    a0 = np.append(eigvec[:, :1].reshape(1, 3), 0)
    a1 = np.append(eigvec[:, 1:2].reshape(1, 3), 0)
    a2 = np.append(eigvec[:, 2:3].reshape(1, 3), 0)
    m = Matrix((a2, a1, a0, (0, 0, 0, 1)))
    # return the rotating ingredients only
    _, rot, _ = m.decompose()
    return rot


class ConvertTo_BaseOperator(Operator):
    @classmethod
    @property
    def type_name(cls):
        return cls.type.name

    @classmethod
    @property
    def bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_convert_to_{cls.type_name.lower()}"

    @classmethod
    @property
    def bl_label(cls):
        return f"Convert object to Modern{cls.type_name}"

    bl_options = {"REGISTER", "UNDO"}
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
        self,
        context: Context,
        obj: Object,
        bbox: BBox,
        mat: Matrix,
    ) -> tuple[Object, Vector]:
        raise NotImplementedError("This method should be implemented by subclass")

    def execute(self, context: Context | None) -> set[str]:
        sel = context.selected_objects.copy()
        # Copy the list because the object may be deleted in the loop
        for obj in sel.copy():
            # bound_box update
            if is_modern_primitive(obj):
                bpy.ops.object.mode_set(mode="OBJECT")
            obj.data.update()

            # 主軸をZ軸へと回転させる為のクォータニオン
            pre_rot: Quaternion
            # _handle Proc method handles the Z axis as height,
            #   so convert it in a timely manner.
            match self.main_axis:
                case "Auto":
                    pre_rot = _auto_axis(get_evaluated_vertices(context, obj))
                    # If the axis mode is Auto,
                    #   an error will be made if the scale value is not uniform
                    #        at this time.
                    if not is_uniform(obj.scale):
                        # If there is only one target object, treat it as an error
                        typ = "WARNING" if len(sel) > 1 else "ERROR"
                        self.report(
                            {typ},
                            f"Couldn't convert \"{obj.name}\" because It didn't have a uniform scaling value",  # noqa: E501
                        )
                        continue

                case "X":
                    # -90 degrees rotation around the Y axis
                    pre_rot = Quaternion(((0, 1, 0)), math.radians(-90))
                case "Y":
                    # 90 degrees around the X-axis
                    pre_rot = Quaternion((1, 0, 0), math.radians(90))
                case "Z":
                    # Do nothing
                    pre_rot = Quaternion()
            mat = pre_rot.to_matrix()

            # get bound_box info (size, average)
            # Z軸を主軸にした場合のバウンディングボックス
            verts = mul_vert_mat(get_evaluated_vertices(context, obj), mat)
            bbox = BBox(verts)
            new_obj, offset = self._handle_proc(context, obj, bbox, mat)
            new_obj.name = obj.name + "_converted"

            new_obj.matrix_world = (
                obj.matrix_world
                @ pre_rot.inverted().to_matrix().to_4x4()
                @ Matrix.Translation(bbox.center)
                @ Matrix.Translation(offset)
            )

            if self.apply_scale:
                bpy.ops.object.mpr_apply_scale(strict=False)

            if not self.keep_original:
                bpy.data.objects.remove(obj)

        return {"FINISHED"}

from bpy.types import Operator, Context, Object
from ..constants import MODERN_PRIMITIVE_PREFIX
from typing import cast
from bpy.props import BoolProperty, EnumProperty
import bpy
from ..aux_func import is_modern_primitive, get_bound_box
from mathutils import Matrix, Vector, Quaternion
import math


class BBox:
    def __init__(self, obj: Object, context: Context, mat: Matrix | None = None):
        (self.min, self.max) = get_bound_box(obj.bound_box, mat)
        self.size = self.max - self.min
        self.center = (self.min + self.max) / 2

    def __str__(self) -> str:
        return f"BBox(min={self.min}, max={self.max},\
size={self.size}, center={self.center})"


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
        default="Z",
        items=(
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
        for obj in sel:
            # bound_box update
            if is_modern_primitive(obj):
                bpy.ops.object.mode_set(mode="OBJECT")
            obj.data.update()

            pre_rot: Quaternion
            # _handle_procメソッドではZ軸を高さとして扱うのでそれに合わせて適時変換する
            match self.main_axis:
                case "X":
                    # Y軸周りに90度回転
                    pre_rot = Quaternion(((0, 1, 0)), math.radians(90))
                case "Y":
                    # X軸周りに-90度回転
                    pre_rot = Quaternion((1, 0, 0), math.radians(-90))
                case "Z":
                    # 何もしない
                    pre_rot = Quaternion()
            mat = pre_rot.to_matrix()

            # get bound_box info (size, average)
            bbox = BBox(obj, context, mat)
            new_obj, offset = self._handle_proc(context, obj, bbox, mat)
            new_obj.name = obj.name + "_converted"

            bbox0 = BBox(obj, context)
            new_obj.matrix_world = (
                obj.matrix_world
                @ Matrix.Translation(bbox0.center)
                @ pre_rot.to_matrix().to_4x4()
                @ Matrix.Translation(offset)
            )

            if self.apply_scale:
                bpy.ops.object.mpr_apply_scale(strict=False)

        if not self.keep_original:
            for obj in sel:
                bpy.data.objects.remove(obj)
        return {"FINISHED"}

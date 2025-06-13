from collections.abc import Callable
from typing import ClassVar

import bmesh
import bpy
from bmesh.types import BMFace
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Context, Event, Object, Operator
from bpy.utils import register_class, unregister_class

from .constants import MODERN_PRIMITIVE_PREFIX
from .convert import (
    ConvertToCapsule_Operator as C_Capsule,
)
from .convert import (
    ConvertToCone_Operator as C_Cone,
)
from .convert import (
    ConvertToCube_Operator as C_Cube,
)
from .convert import (
    ConvertToCylinder_Operator as C_Cylinder,
)
from .convert import (
    ConvertToGrid_Operator as C_Grid,
)
from .convert import (
    ConvertToSphere_Operator as C_Sphere,
)
from .convert import (
    ConvertToTorus_Operator as C_Torus,
)
from .convert import (
    ConvertToTube_Operator as C_Tube,
)
from .convert.convert_to_baseop import ConvertTo_BaseOperator
from .exception import DGException, DGInvalidInput
from .util.aux_func import get_object_just_added
from .util.aux_other import make_bmesh
from .util.union_find import UnionFind


def _get_ops(op: type[ConvertTo_BaseOperator]) -> Callable[[...], None]:
    return getattr(bpy.ops.mesh, op.bl_idname.split(".")[1])


PROC: dict[str, Callable[[...], None]] = {
    "Cube": _get_ops(C_Cube),
    "DCube": lambda **kwargs: _get_ops(C_Cube)(cube_type="DeformableCube", **kwargs),
    "Grid": _get_ops(C_Grid),
    "UV Sphere": lambda **kwargs: _get_ops(C_Sphere)(sphere_type="UVSphere", **kwargs),
    "ICO Sphere": lambda **kwargs: _get_ops(C_Sphere)(sphere_type="ICOSphere", **kwargs),
    "Quad Sphere": lambda **kwargs: _get_ops(C_Sphere)(sphere_type="QuadSphere", **kwargs),
    "Cylinder": _get_ops(C_Cylinder),
    "Cone": _get_ops(C_Cone),
    "Torus": _get_ops(C_Torus),
    "Tube": _get_ops(C_Tube),
    "Capsule": _get_ops(C_Capsule),
}


class DGConvertFailed(DGException):
    pass


class ExtractPrimitive_Operator(Operator):
    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_extract_primitive"
    bl_label = "Make Primitive From Selected Polygon"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    primitive_type: EnumProperty(
        name="Primitive Type",
        default="Cube",
        items=(
            ("Cube", "Cube", ""),
            ("DCube", "D-Cube", ""),
            ("Grid", "Grid", ""),
            ("UV Sphere", "UV Sphere", ""),
            ("ICO Sphere", "ICO Sphere", ""),
            ("Quad Sphere", "Quad Sphere", ""),
            ("Cylinder", "Cylinder", ""),
            ("Cone", "Cone", ""),
            ("Torus", "Torus", ""),
            ("Tube", "Tube", ""),
            ("Capsule", "Capsule", ""),
        ),
    )
    keep_original_mesh: BoolProperty(
        name="Keep Original Mesh",
        default=False,
    )
    fill_hole: BoolProperty(
        name="Fill Hole",
        default=True,
    )
    postfix: StringProperty(
        name="Postfix",
        default="_extracted",
    )

    def draw(self, context: Context) -> None:
        lo = self.layout
        lo.prop(self, "primitive_type")
        lo.prop(self, "keep_original_mesh")
        if not self.keep_original_mesh:
            lo.prop(self, "fill_hole")
        lo.prop(self, "postfix")

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        # For now, only object mode is supported
        if context.mode not in ("OBJECT", "EDIT_MESH"):
            return False
        # All selected objects are mesh?
        return all(obj.type == "MESH" for obj in context.selected_objects)

    def invoke(self, context: Context, event: Event) -> set[str]:
        self.keep_original_mesh = event.shift
        return self.execute(context)

    @staticmethod
    def _make_convex_from_faces(faces: set[BMFace], obj: Object) -> Object:
        # Copy Select Face to New BMesh
        new_bm = bmesh.new()

        for face in faces:
            new_face_verts = []
            for v in face.verts:
                # Create vertex (if not available)
                try:
                    nv = new_bm.verts[v.index]
                except IndexError:
                    nv = new_bm.verts.new(v.co)

                new_face_verts.append(nv)
            new_face = new_bm.faces.new(new_face_verts)
            new_face.smooth = face.smooth

        # Make Convex-Hull
        bmesh.ops.convex_hull(new_bm, input=new_bm.verts)

        # Save as new mesh data
        new_mesh = bpy.data.meshes.new(obj.name + "_selected_faces")
        new_bm.to_mesh(new_mesh)
        new_bm.free()

        new_mesh.update()

        # Add as a new object
        new_obj = bpy.data.objects.new(obj.name, new_mesh)

        # Place in the same position as the original
        new_obj.matrix_world = obj.matrix_world
        return new_obj

    def _make_convex(self, obj: Object) -> list[Object]:
        ret: list[Object] = []
        with make_bmesh(obj.data, False) as bm:
            selected_faces = [f for f in bm.faces if f.select]
            if len(selected_faces) == 0:
                raise DGInvalidInput("no selected faces")

            uf_face: list[BMFace] = []
            faceidx_to_ufidx: dict[int, int] = {}

            for idx, f in enumerate(selected_faces):
                uf_face.append(f)
                faceidx_to_ufidx[f.index] = idx

            # Grouping with union-find algorithm
            uf = UnionFind(len(uf_face))
            for f in uf_face:
                for e in f.edges:
                    for f2 in e.link_faces:
                        if not f2.select:
                            continue
                        if f == f2:
                            continue
                        uf.connect(faceidx_to_ufidx[f.index], faceidx_to_ufidx[f2.index])

            groups = uf.get_groups()
            for g in groups:
                group_faces = [uf_face[ufid] for ufid in g]
                new_obj = self._make_convex_from_faces(group_faces, obj)

                # Delete original polygons (if needed)
                if not self.keep_original_mesh:
                    if self.fill_hole:
                        # Store the edges
                        # associated with the face to reselect edges before deleting
                        related_edges = {e for f in group_faces for e in f.edges}

                    # Delete Faces
                    bmesh.ops.delete(bm, geom=group_faces, context="FACES")

                    if self.fill_hole:
                        # After deletion, select the edges used for the original face
                        for e in bm.edges:
                            # Select only non-manifold edges
                            e.select_set(e in related_edges and not e.is_manifold)
                        # Fill the face
                        bmesh.ops.holes_fill(
                            bm, edges=[e for e in bm.edges if e.select], sides=0
                        )
                ret.append(new_obj)
        return ret

    def _make_primitive(self, context: Context, convex: Object) -> Object:
        # Postfix something appropriately
        # prev_name = convex.name
        with context.temp_override(
            active_object=convex, object=convex, selected_objects=[convex]
        ):
            # Crash if we don't leave the source
            proc = PROC[self.primitive_type]
            proc(keep_original=True, postfix=self.postfix)

            try:
                return get_object_just_added(context)
                # return bpy.data.objects[prev_name + self.postfix]
            except KeyError as e:
                raise DGConvertFailed() from e

    def execute(self, context: Context | None) -> set[str]:
        new_objs: list[Object] = []

        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # If we don't update explicitly,
        # object.location and object.matrix world may be different
        context.view_layer.update()
        for obj in context.selected_objects:
            try:
                convex_s = self._make_convex(obj)
                for c in convex_s:
                    context.collection.objects.link(c)

                    new_obj = self._make_primitive(context, c)
                    new_objs.append(new_obj)

                    bpy.data.objects.remove(c)

            except DGInvalidInput as e:
                print(e)
            except DGConvertFailed:
                print("Convert failed")

        bpy.ops.object.select_all(action="DESELECT")
        print(new_objs)
        for obj in new_objs:
            obj.select_set(True)

        self.report({"INFO"}, f"{len(new_objs)} Object(s) Converted.")
        return {"FINISHED"}


def register() -> None:
    register_class(ExtractPrimitive_Operator)


def unregister() -> None:
    unregister_class(ExtractPrimitive_Operator)

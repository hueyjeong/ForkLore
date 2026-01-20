"""
MapService - Business logic for Map management.
"""

import builtins

from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, QuerySet

from apps.contents.models import (
    LayerType,
    Map,
    MapLayer,
    MapObject,
    MapSnapshot,
    WikiEntry,
)
from apps.novels.models import Branch
from apps.users.models import User


class MapService:
    """Service for managing maps, snapshots, layers, and objects."""

    @staticmethod
    def _check_branch_author(branch: Branch, user: User) -> None:
        """Check if user is the branch author."""
        if branch.author_id != user.id:
            raise PermissionDenied("브랜치 작가만 수정할 수 있습니다.")

    @staticmethod
    def create(
        branch_id: int,
        user: User,
        name: str,
        width: int,
        height: int,
        description: str = "",
    ) -> Map:
        """
        Create a new map.

        Args:
            branch_id: Branch ID
            user: User creating the map
            name: Map name
            width: Map width in pixels
            height: Map height in pixels
            description: Map description (optional)

        Returns:
            Created Map instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If branch not found or map with same name exists
        """
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist as e:
            raise ValueError("존재하지 않는 브랜치입니다.") from e

        MapService._check_branch_author(branch, user)

        # Check for duplicate name
        if Map.objects.filter(branch=branch, name=name).exists():
            raise ValueError(f"이미 존재하는 지도 이름입니다: {name}")

        return Map.objects.create(
            branch=branch,
            name=name,
            description=description,
            width=width,
            height=height,
        )

    @staticmethod
    def update(
        map_id: int,
        user: User,
        name: str | None = None,
        description: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> Map:
        """
        Update a map.

        Args:
            map_id: Map ID
            user: User performing the update
            name: New name (optional)
            description: New description (optional)
            width: New width (optional)
            height: New height (optional)

        Returns:
            Updated Map instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If map not found
        """
        try:
            map_obj = Map.objects.select_related("branch").get(id=map_id)
        except Map.DoesNotExist as e:
            raise ValueError("존재하지 않는 지도입니다.") from e

        MapService._check_branch_author(map_obj.branch, user)

        if name is not None:
            map_obj.name = name
        if description is not None:
            map_obj.description = description
        if width is not None:
            map_obj.width = width
        if height is not None:
            map_obj.height = height

        map_obj.save()
        return map_obj

    @staticmethod
    def retrieve(map_id: int) -> Map:
        """
        Fetches the Map with the given ID.
        
        Parameters:
            map_id (int): ID of the Map to fetch.
        
        Returns:
            Map: The Map instance with snapshots, layers, and map_objects prefetched.
        
        Raises:
            ValueError: If no Map with the given ID exists.
        """
        try:
            return Map.objects.prefetch_related("snapshots__layers__map_objects").get(id=map_id)
        except Map.DoesNotExist as e:
            raise ValueError("존재하지 않는 지도입니다.") from e

    @staticmethod
    def list(branch_id: int) -> QuerySet[Map]:
        """
        List maps for a branch.

        Args:
            branch_id: Branch ID

        Returns:
            QuerySet of Map
        """
        return Map.objects.filter(branch_id=branch_id).order_by("name")

    @staticmethod
    def delete(map_id: int, user: User) -> None:
        """
        Delete a map.

        Args:
            map_id: Map ID
            user: User performing the deletion

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If map not found
        """
        try:
            map_obj = Map.objects.select_related("branch").get(id=map_id)
        except Map.DoesNotExist as e:
            raise ValueError("존재하지 않는 지도입니다.") from e

        MapService._check_branch_author(map_obj.branch, user)
        map_obj.delete()

    # --- Snapshot Methods ---

    @staticmethod
    def create_snapshot(
        map_id: int,
        user: User,
        valid_from_chapter: int,
        base_image_url: str = "",
    ) -> MapSnapshot:
        """
        Create a new MapSnapshot for a map that becomes effective from a specific chapter.
        
        Parameters:
            map_id (int): ID of the map to attach the snapshot to.
            user (User): User creating the snapshot.
            valid_from_chapter (int): Chapter number from which this snapshot is effective (inclusive).
            base_image_url (str): Optional base image URL for the snapshot.
        
        Returns:
            MapSnapshot: The created MapSnapshot, reloaded with its layers prefetched.
        
        Raises:
            PermissionDenied: If the user is not the author of the map's branch.
            ValueError: If the map does not exist or a snapshot for the given chapter already exists.
        """
        try:
            map_obj = Map.objects.select_related("branch").get(id=map_id)
        except Map.DoesNotExist as e:
            raise ValueError("존재하지 않는 지도입니다.") from e

        MapService._check_branch_author(map_obj.branch, user)

        # Check for existing snapshot at this chapter
        if MapSnapshot.objects.filter(map=map_obj, valid_from_chapter=valid_from_chapter).exists():
            raise ValueError(f"이미 회차 {valid_from_chapter}에 스냅샷이 존재합니다.")

        snapshot = MapSnapshot.objects.create(
            map=map_obj,
            valid_from_chapter=valid_from_chapter,
            base_image_url=base_image_url,
        )
        # Reload with prefetch to avoid N+1 when serializer accesses layers
        return MapSnapshot.objects.prefetch_related("layers").get(id=snapshot.id)

    @staticmethod
    def get_snapshot_for_chapter(map_id: int, chapter_number: int) -> MapSnapshot | None:
        """
        Return the MapSnapshot for which valid_from_chapter is the largest value less than or equal to chapter_number for the specified map.
        
        Returns:
            MapSnapshot | None: The matching MapSnapshot, or None if no snapshot applies.
        """
        return (
            MapSnapshot.objects.filter(
                map_id=map_id,
                valid_from_chapter__lte=chapter_number,
            )
            .prefetch_related(
                Prefetch("layers", queryset=MapLayer.objects.prefetch_related("map_objects"))
            )
            .order_by("-valid_from_chapter")
            .first()
        )

    @staticmethod
    def get_for_chapter(map_id: int, chapter_number: int) -> dict:
        """
        Get map with context-aware snapshot for a specific chapter.

        Args:
            map_id: Map ID
            chapter_number: Current chapter being read

        Returns:
            Dict with 'map' and 'snapshot' keys

        Raises:
            ValueError: If map not found
        """
        map_obj = MapService.retrieve(map_id)
        snapshot = MapService.get_snapshot_for_chapter(map_id, chapter_number)

        return {
            "map": map_obj,
            "snapshot": snapshot,
        }

    # --- Layer Methods ---

    @staticmethod
    def add_layer(
        snapshot_id: int,
        user: User,
        name: str,
        layer_type: str = LayerType.OVERLAY,
        z_index: int = 0,
        is_visible: bool = True,
        style_json: dict | None = None,
    ) -> MapLayer:
        """
        Add a layer to a map snapshot.

        Args:
            snapshot_id: MapSnapshot ID
            user: User creating the layer
            name: Layer name
            layer_type: Layer type (BASE, OVERLAY, MARKER, PATH, REGION)
            z_index: Z-order for rendering
            is_visible: Whether layer is visible by default
            style_json: Layer style JSON (optional)

        Returns:
            Created MapLayer instance

        Raises:
            PermissionDenied: If user is not branch author
            ValueError: If snapshot not found
        """
        try:
            snapshot = MapSnapshot.objects.select_related("map__branch").get(id=snapshot_id)
        except MapSnapshot.DoesNotExist as e:
            raise ValueError("존재하지 않는 스냅샷입니다.") from e

        MapService._check_branch_author(snapshot.map.branch, user)

        layer = MapLayer.objects.create(
            snapshot=snapshot,
            name=name,
            layer_type=layer_type,
            z_index=z_index,
            is_visible=is_visible,
            style_json=style_json,
        )
        # Reload with prefetch to avoid N+1 when serializer accesses map_objects
        return MapLayer.objects.prefetch_related("map_objects").get(id=layer.id)

    @staticmethod
    def update_layer(
        layer_id: int,
        user: User,
        name: str | None = None,
        layer_type: str | None = None,
        z_index: int | None = None,
        is_visible: bool | None = None,
        style_json: dict | None = None,
    ) -> MapLayer:
        """
        Update fields of an existing map layer.
        
        Parameters:
            layer_id (int): ID of the MapLayer to update.
            user (User): User performing the update; must be the author of the layer's branch.
            name (str | None): New name for the layer.
            layer_type (str | None): New layer type.
            z_index (int | None): New stacking order value.
            is_visible (bool | None): New visibility flag.
            style_json (dict | None): New style definition as a JSON-compatible dict.
        
        Returns:
            MapLayer: The updated MapLayer instance.
        """
        try:
            layer = MapLayer.objects.select_related("snapshot__map__branch").get(id=layer_id)
        except MapLayer.DoesNotExist as e:
            raise ValueError("존재하지 않는 레이어입니다.") from e

        MapService._check_branch_author(layer.snapshot.map.branch, user)

        if name is not None:
            layer.name = name
        if layer_type is not None:
            layer.layer_type = layer_type
        if z_index is not None:
            layer.z_index = z_index
        if is_visible is not None:
            layer.is_visible = is_visible
        if style_json is not None:
            layer.style_json = style_json

        layer.save()
        return layer

    @staticmethod
    def delete_layer(layer_id: int, user: User) -> None:
        """Delete a map layer."""
        try:
            layer = MapLayer.objects.select_related("snapshot__map__branch").get(id=layer_id)
        except MapLayer.DoesNotExist as e:
            raise ValueError("존재하지 않는 레이어입니다.") from e

        MapService._check_branch_author(layer.snapshot.map.branch, user)
        layer.delete()

    # --- Object Methods ---

    @staticmethod
    def add_object(
        layer_id: int,
        user: User,
        object_type: str,
        coordinates: dict,
        label: str = "",
        description: str = "",
        wiki_entry_id: int | None = None,
        style_json: dict | None = None,
    ) -> MapObject:
        """
        Add an object to a map layer.

        Args:
            layer_id: MapLayer ID
            user: User creating the object
            object_type: Object type (POINT, LINE, POLYGON, CIRCLE, ICON)
            coordinates: Object coordinates (JSON)
            label: Object label (optional)
            description: Object description (optional)
            wiki_entry_id: Linked WikiEntry ID (optional)
            style_json: Object style JSON (optional)

        Returns:
            Created MapObject instance
        """
        try:
            layer = MapLayer.objects.select_related("snapshot__map__branch").get(id=layer_id)
        except MapLayer.DoesNotExist as e:
            raise ValueError("존재하지 않는 레이어입니다.") from e

        MapService._check_branch_author(layer.snapshot.map.branch, user)

        wiki_entry = None
        if wiki_entry_id:
            try:
                wiki_entry = WikiEntry.objects.get(id=wiki_entry_id)
            except WikiEntry.DoesNotExist as e:
                raise ValueError("존재하지 않는 위키입니다.") from e

        return MapObject.objects.create(
            layer=layer,
            object_type=object_type,
            coordinates=coordinates,
            label=label,
            description=description,
            wiki_entry=wiki_entry,
            style_json=style_json,
        )

    @staticmethod
    def update_object(
        object_id: int,
        user: User,
        object_type: str | None = None,
        coordinates: dict | None = None,
        label: str | None = None,
        description: str | None = None,
        wiki_entry_id: int | None = None,
        style_json: dict | None = None,
    ) -> MapObject:
        """Update a map object."""
        try:
            obj = MapObject.objects.select_related("layer__snapshot__map__branch").get(id=object_id)
        except MapObject.DoesNotExist as e:
            raise ValueError("존재하지 않는 오브젝트입니다.") from e

        MapService._check_branch_author(obj.layer.snapshot.map.branch, user)

        if object_type is not None:
            obj.object_type = object_type
        if coordinates is not None:
            obj.coordinates = coordinates
        if label is not None:
            obj.label = label
        if description is not None:
            obj.description = description
        if wiki_entry_id is not None:
            try:
                obj.wiki_entry = WikiEntry.objects.get(id=wiki_entry_id)
            except WikiEntry.DoesNotExist as e:
                raise ValueError("존재하지 않는 위키입니다.") from e
        if style_json is not None:
            obj.style_json = style_json

        obj.save()
        return obj

    @staticmethod
    def delete_object(object_id: int, user: User) -> None:
        """Delete a map object."""
        try:
            obj = MapObject.objects.select_related("layer__snapshot__map__branch").get(id=object_id)
        except MapObject.DoesNotExist as e:
            raise ValueError("존재하지 않는 오브젝트입니다.") from e

        MapService._check_branch_author(obj.layer.snapshot.map.branch, user)
        obj.delete()

    # --- Fork Methods ---

    @staticmethod
    def fork_maps(
        source_branch_id: int,
        target_branch_id: int,
        user: User,
    ) -> builtins.list[Map]:
        """
        Fork all maps from source branch to target branch.

        This copies:
        - All Maps (with source_map reference)
        - All MapSnapshots
        - All MapLayers
        - All MapObjects

        Args:
            source_branch_id: Source branch ID
            target_branch_id: Target branch ID
            user: User performing the fork

        Returns:
            List of created Map instances
        """
        try:
            source_branch = Branch.objects.get(id=source_branch_id)
            target_branch = Branch.objects.get(id=target_branch_id)
        except Branch.DoesNotExist as e:
            raise ValueError("존재하지 않는 브랜치입니다.") from e

        forked_maps = []
        source_maps = Map.objects.filter(branch=source_branch).prefetch_related(
            Prefetch(
                "snapshots",
                queryset=MapSnapshot.objects.prefetch_related(
                    Prefetch("layers", queryset=MapLayer.objects.prefetch_related("map_objects"))
                ),
            )
        )

        for source_map in source_maps:
            # Create new map with source reference
            new_map = Map.objects.create(
                branch=target_branch,
                source_map=source_map,
                name=source_map.name,
                description=source_map.description,
                width=source_map.width,
                height=source_map.height,
            )

            # Copy snapshots
            for source_snapshot in source_map.snapshots.all():
                new_snapshot = MapSnapshot.objects.create(
                    map=new_map,
                    valid_from_chapter=source_snapshot.valid_from_chapter,
                    base_image_url=source_snapshot.base_image_url,
                )

                # Copy layers
                for source_layer in source_snapshot.layers.all():
                    new_layer = MapLayer.objects.create(
                        snapshot=new_snapshot,
                        name=source_layer.name,
                        layer_type=source_layer.layer_type,
                        z_index=source_layer.z_index,
                        is_visible=source_layer.is_visible,
                        style_json=source_layer.style_json,
                    )

                    # Copy objects
                    for source_obj in source_layer.map_objects.all():
                        MapObject.objects.create(
                            layer=new_layer,
                            object_type=source_obj.object_type,
                            coordinates=source_obj.coordinates,
                            label=source_obj.label,
                            description=source_obj.description,
                            wiki_entry=source_obj.wiki_entry,
                            style_json=source_obj.style_json,
                        )

            forked_maps.append(new_map)

        return forked_maps
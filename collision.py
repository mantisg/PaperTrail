import pygame
import os
from weakref import WeakKeyDictionary
from asset_manager import get_asset_path

# Cache masks and partial masks per object to avoid regenerating each frame
_mask_cache = WeakKeyDictionary()
_partial_cache = WeakKeyDictionary()


def _load_surface_from(obj):
    """Return a pygame.Surface for the given object if possible.

    Supports objects providing `get_image()`, a `_image` attribute, or an `image_path`.
    """
    if hasattr(obj, 'get_image'):
        try:
            return obj.get_image()
        except Exception:
            pass
    if hasattr(obj, '_image') and obj._image is not None:
        return obj._image
    if hasattr(obj, 'image_path') and obj.image_path:
        path = obj.image_path
        if (not os.path.isabs(path)) and (not os.path.exists(path)):
            path = get_asset_path(os.path.basename(path))
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return None
    return None


def get_mask(obj):
    """Return a pygame.mask.Mask for `obj`, caching the result."""
    if obj in _mask_cache:
        return _mask_cache[obj]
    surf = _load_surface_from(obj)
    if surf is None:
        return None
    mask = pygame.mask.from_surface(surf)
    _mask_cache[obj] = mask
    return mask


def get_partial_mask(obj, fraction=1/3):
    """Return a bottom-portion mask (fraction of height) for `obj`, cached."""
    d = _partial_cache.setdefault(obj, {})
    if fraction in d:
        return d[fraction]
    full = get_mask(obj)
    if full is None:
        return None
    w, h = full.get_size()
    part_h = max(1, int(h * fraction))
    partial = pygame.mask.Mask((w, part_h))
    for y in range(part_h):
        for x in range(w):
            src_y = h - part_h + y
            if full.get_at((x, src_y)):
                partial.set_at((x, y), True)
    d[fraction] = partial
    return partial


def mask_vs_object(other_mask, other_pos, obj, use_obj_partial=False, fraction=1/3):
    """Check overlap between an external mask (other_mask) at other_pos and an object `obj`.

    This mirrors the old `GameObject.overlaps(other_pos, other_mask)` API but centralizes logic.
    """
    if other_mask is None:
        return False
    obj_mask = get_partial_mask(obj, fraction) if use_obj_partial else get_mask(obj)
    if obj_mask is None:
        return False

    surf = _load_surface_from(obj)
    if surf is None:
        return False

    # Rect for this object centered at its position
    try:
        obj_pos = obj.pos
    except Exception:
        # Fallback: place rect at origin
        obj_pos = pygame.Vector2(0, 0)

    rect_obj = surf.get_rect(center=(int(obj_pos.x), int(obj_pos.y)))
    if use_obj_partial:
        rect_obj.y = int(obj_pos.y + surf.get_height() / 3)

    # rect for other mask (mask doesn't carry a surface size, so use mask size)
    other_size = other_mask.get_size()
    rect_other = pygame.Rect(int(other_pos.x - other_size[0] / 2),
                             int(other_pos.y - other_size[1] / 2),
                             other_size[0], other_size[1])

    if not rect_obj.colliderect(rect_other):
        return False

    offset = (rect_other.x - rect_obj.x, rect_other.y - rect_obj.y)
    try:
        return obj_mask.overlap(other_mask, offset) is not None
    except Exception:
        return True


def objects_overlap(a, pos_a, b, pos_b, use_a_partial=False, use_b_partial=False, fraction=1/3):
    """Check overlap between two objects `a` and `b` at their positions.

    Both objects can be game entities (with `get_image`/`image_path`) or surfaces.
    """
    mask_a = get_partial_mask(a, fraction) if use_a_partial else get_mask(a)
    mask_b = get_partial_mask(b, fraction) if use_b_partial else get_mask(b)
    if mask_a is None or mask_b is None:
        return False

    surf_a = _load_surface_from(a)
    surf_b = _load_surface_from(b)
    if surf_a is None or surf_b is None:
        return False

    rect_a = surf_a.get_rect(center=(int(pos_a.x), int(pos_a.y)))
    rect_b = surf_b.get_rect(center=(int(pos_b.x), int(pos_b.y)))
    if use_a_partial:
        rect_a.y = int(pos_a.y + surf_a.get_height() / 3)
    if use_b_partial:
        rect_b.y = int(pos_b.y + surf_b.get_height() / 3)

    if not rect_a.colliderect(rect_b):
        return False

    offset = (rect_b.x - rect_a.x, rect_b.y - rect_a.y)
    try:
        return mask_a.overlap(mask_b, offset) is not None
    except Exception:
        return True

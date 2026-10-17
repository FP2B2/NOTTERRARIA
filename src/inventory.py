"""
Player inventory, 10-slot hotbar, and item management.
Provides structured summaries for LLM context injection.
"""

from typing import List, Optional, Dict
from .items import ITEM_REGISTRY, ItemDef


class ItemStack:
    def __init__(self, item_id: str, count: int = 1):
        self.item_id = item_id
        self.count = count

    @property
    def item_def(self) -> Optional[ItemDef]:
        return ITEM_REGISTRY.get(self.item_id)


class Inventory:
    def __init__(self, hotbar_size: int = 10, total_slots: int = 40):
        self.hotbar_size = hotbar_size
        self.total_slots = total_slots
        self.slots: List[Optional[ItemStack]] = [None] * total_slots
        self.selected_slot: int = 0  # 0 to 9

        # Give starting Copper Loadout (Sword equipped in slot 0)
        self.slots[0] = ItemStack("copper_shortsword", 1)
        self.slots[1] = ItemStack("copper_pickaxe", 1)
        self.slots[2] = ItemStack("copper_axe", 1)
        self.slots[3] = ItemStack("torch", 15)
        self.slots[4] = ItemStack("wood", 20)

    def select_slot(self, index: int):
        if 0 <= index < self.hotbar_size:
            self.selected_slot = index

    def get_selected(self) -> Optional[ItemStack]:
        return self.slots[self.selected_slot]

    def add_item(self, item_id: str, count: int = 1) -> int:
        """Adds an item to existing stacks first, then to empty slots. Returns leftover count."""
        item_def = ITEM_REGISTRY.get(item_id)
        if not item_def:
            return count

        # 1. Fill existing matching stacks
        for slot in self.slots:
            if slot and slot.item_id == item_id:
                space = item_def.max_stack - slot.count
                if space > 0:
                    add_amt = min(space, count)
                    slot.count += add_amt
                    count -= add_amt
                    if count <= 0:
                        return 0

        # 2. Place into empty slots
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                add_amt = min(item_def.max_stack, count)
                self.slots[i] = ItemStack(item_id, add_amt)
                count -= add_amt
                if count <= 0:
                    return 0

        return count  # Overflow

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        """Removes the given quantity of an item across slots if available."""
        if not self.has_item(item_id, count):
            return False

        remaining_to_remove = count
        for i in range(len(self.slots)):
            slot = self.slots[i]
            if slot and slot.item_id == item_id:
                if slot.count <= remaining_to_remove:
                    remaining_to_remove -= slot.count
                    self.slots[i] = None
                else:
                    slot.count -= remaining_to_remove
                    remaining_to_remove = 0
                if remaining_to_remove <= 0:
                    break
        return True

    def has_item(self, item_id: str, count: int = 1) -> bool:
        total = sum(slot.count for slot in self.slots if slot and slot.item_id == item_id)
        return total >= count

    def get_summary_for_ai(self) -> str:
        """Generates a clean string summary of all items the player carries, formatted for LLM prompts."""
        carried: Dict[str, int] = {}
        for slot in self.slots:
            if slot:
                name = slot.item_def.name if slot.item_def else slot.item_id
                carried[name] = carried.get(name, 0) + slot.count

        if not carried:
            return "Inventory is empty."

        items_str = ", ".join(f"{count}x {name}" for name, count in carried.items())
        return f"Carrying: {items_str}"

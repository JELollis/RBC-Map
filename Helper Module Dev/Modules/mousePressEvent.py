# Copyright 2024 RBC Community Map Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
def mousePressEvent(self, event):
    """
    Handle mouse press event to update the minimap location.

    Centers the clicked cell within the minimap, adjusting for the current zoom level.

    Args:
        event (QMouseEvent): The mouse event containing the position of the click.
    """
    # Check if click occurred within minimap boundaries
    if 0 <= event.position().x() < self.minimap_label.width() and 0 <= event.position().y() < self.minimap_label.height():
        # Get click coordinates within minimap
        x = event.position().x()
        y = event.position().y()

        # Determine the size of each minimap cell based on zoom level
        block_size = self.minimap_size // self.zoom_level

        # Calculate the minimap coordinates (column and row) of the clicked cell
        col_clicked = int(x // block_size)
        row_clicked = int(y // block_size)

        # Calculate the exact map column/row positions, centering the clicked cell
        self.column_start = max(0, self.column_start + col_clicked - (self.zoom_level // 2))
        self.row_start = max(0, self.row_start + row_clicked - (self.zoom_level // 2))

        # Ensure `column_start` and `row_start` don't exceed map boundaries
        max_bound = 200 - self.zoom_level  # Adjust max bound for edge cases
        self.column_start = min(self.column_start, max_bound)
        self.row_start = min(self.row_start, max_bound)

        # Update the minimap to reflect the new center position
        self.update_minimap()

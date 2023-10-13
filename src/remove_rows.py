def remove_selected_rows(self):
    selected_rows = set(index.row() for index in self.table_widget.selectionModel().selectedRows())
    for row in sorted(selected_rows, reverse=True):
        # Get the ID of the row being removed
        row_id = self.table_widget.item(row, 0).text()
        print(f"Right-clicked on row ID: {row_id}")
        # Remove the row from the table
        self.table_widget.removeRow(row)
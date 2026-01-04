from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
import os

class Ui_BQManager(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        # Load UI from .ui file for layout editing
        from PyQt5 import uic
        import os
        ui_path = os.path.join(os.path.dirname(__file__), 'BQ_Manager.ui')
        uic.loadUi(ui_path, self)

        # Ensure widgets exist and set defaults
        # Setup filter combo
        try:
            self.combo_filter_field.clear()
            self.combo_filter_field.addItems(["BQ ID", "Bill", "Section", "Page", "Item", "Description", "Trade"])
        except Exception:
            pass

        # Setup sort combo
        try:
            self.combo_sort_field.clear()
            self.combo_sort_field.addItems(["BQ ID", "Bill", "Section", "Page", "Item", "Qty", "Rate", "Amount", "Trade"])
        except Exception:
            pass

        # Table setup
        try:
            self.table.setColumnCount(13)
            self.table.setHorizontalHeaderLabels([
                "BQ ID", "Bill", "Section", "Page", "Item", "Description",
                "Qty", "Unit", "Rate", "Discount", "Amount", "Trade", "Remark"
            ])
            self.table.horizontalHeader().sectionClicked.connect(self.on_header_sort)
            self.table.itemChanged.connect(self.on_table_item_changed)
        except Exception:
            pass

        # Connect signals
        try:
            self.btn_import.clicked.connect(self.import_excel)
            self.btn_export.clicked.connect(self.export_excel)
            self.btn_add.clicked.connect(self.add_item)
            self.btn_delete.clicked.connect(self.delete_item)
            self.btn_refresh.clicked.connect(self.refresh_table)
            self.btn_apply_filter.clicked.connect(self.refresh_table)
            self.btn_sort_toggle.clicked.connect(self.toggle_sort_order)
        except Exception:
            pass

        self._col_sort_map = {
            0: 'BQ ID', 1: 'Bill', 2: 'Section', 3: 'Page', 4: 'Item', 6: 'Qty', 8: 'Rate', 10: 'Amount', 11: 'Trade'
        }

        # Sorting state
        self.sort_ascending = True

        # Initial load
        self.refresh_table()

    def format_number(self, value):
        try:
            return "{:,.2f}".format(float(value))
        except Exception:
            return "0.00"

    def refresh_table(self):
        items = self.manager.get_all_bq_items()

        # Disable table sorting, header signals and itemChanged while populating to avoid re-entrancy
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().blockSignals(True)
        # Block all table signals (including itemChanged) while filling
        self.table.blockSignals(True)

        try:
            # Apply filter if any
            filter_field = self.combo_filter_field.currentText()
            filter_text = self.edit_filter.text().strip().lower()
            if filter_text:
                def matches(it):
                    mapping = {
                        'BQ ID': lambda x: str(x.get('BQ ID', '')).lower(),
                        'Bill': lambda x: str(x.get('Bill', '')).lower(),
                        'Section': lambda x: str(x.get('Section', '')).lower(),
                        'Page': lambda x: str(x.get('Page', '')).lower(),
                        'Item': lambda x: str(x.get('Item', '')).lower(),
                        'Description': lambda x: str(x.get('description', '')).lower(),
                        'Trade': lambda x: str(x.get('Trade', '')).lower()
                    }
                    getter = mapping.get(filter_field, lambda x: '')
                    return filter_text in getter(it)
                items = [it for it in items if matches(it)]

            # Apply sorting
            sort_field = self.combo_sort_field.currentText()
            key_map = {
                'BQ ID': lambda x: x.get('BQ ID', ''),
                'Bill': lambda x: x.get('Bill', ''),
                'Section': lambda x: x.get('Section', ''),
                'Page': lambda x: x.get('Page', ''),
                'Item': lambda x: x.get('Item', ''),
                'Qty': lambda x: float(x.get('Qty') or 0),
                'Rate': lambda x: float(x.get('Rate') or 0),
                'Amount': lambda x: float((x.get('Qty') or 0) * (x.get('Rate') or 0) * (1 - (x.get('Discount') or 0))),
                'Trade': lambda x: x.get('Trade', '')
            }
            keyfunc = key_map.get(sort_field, lambda x: x.get('BQ ID', ''))
            items = sorted(items, key=keyfunc, reverse=not self.sort_ascending)

            # Populate table and compute filtered total amount
            total_amount = 0.0
            self.table.setRowCount(len(items))
            for row, item in enumerate(items):
                self.table.setItem(row, 0, QTableWidgetItem(item.get("BQ ID", "")))
                self.table.setItem(row, 1, QTableWidgetItem(item.get("Bill", "")))
                self.table.setItem(row, 2, QTableWidgetItem(item.get("Section", "")))
                self.table.setItem(row, 3, QTableWidgetItem(item.get("Page", "")))
                self.table.setItem(row, 4, QTableWidgetItem(item.get("Item", "")))
                self.table.setItem(row, 5, QTableWidgetItem(item.get("description", "")))
                self.table.setItem(row, 6, QTableWidgetItem(str(item.get("Qty", ""))))
                self.table.setItem(row, 7, QTableWidgetItem(item.get("Unit", "")))
                self.table.setItem(row, 8, QTableWidgetItem(str(item.get("Rate", ""))))
                self.table.setItem(row, 9, QTableWidgetItem(str(item.get("Discount", ""))))

                # Calculate amount = Qty * Rate * (1 - Discount)
                try:
                    qty = float(item.get('Qty') or 0)
                    rate = float(item.get('Rate') or 0)
                    discount = float(item.get('Discount') or 0)
                    amount = qty * rate * (1 - discount)
                except Exception:
                    amount = 0.0
                total_amount += amount
                self.table.setItem(row, 10, QTableWidgetItem(self.format_number(amount)))

                self.table.setItem(row, 11, QTableWidgetItem(item.get("Trade", "")))
                self.table.setItem(row, 12, QTableWidgetItem(item.get("Remark", "")))

            # Update filtered total amount label
            self.label_total_amount.setText(f"Total Amount: {self.format_number(total_amount)}")
        finally:
            # Re-enable header signals, sorting and table signals
            self.table.horizontalHeader().blockSignals(False)
            self.table.setSortingEnabled(True)
            self.table.blockSignals(False)

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            try:
                count = self.manager.import_from_excel(file_path)
                self.refresh_table()
                QMessageBox.information(self, "Success", f"Imported {count} records successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import: {str(e)}")

    def toggle_sort_order(self):
        # Toggle ascending/descending and update button text
        self.sort_ascending = not self.sort_ascending
        self.btn_sort_toggle.setText("Asc" if self.sort_ascending else "Desc")
        self.refresh_table()

    def on_header_sort(self, logicalIndex):
        """Handle header click to sort by that column. Toggle order if same column clicked."""
        # Map column to field if known
        sort_field = self._col_sort_map.get(logicalIndex)
        if not sort_field:
            # Column not mapped for sorting; ignore
            return

        current_sort = self.combo_sort_field.currentText()
        if current_sort == sort_field:
            # Toggle order
            self.sort_ascending = not self.sort_ascending
            self.btn_sort_toggle.setText("Asc" if self.sort_ascending else "Desc")
        else:
            # Change sort field and reset to ascending
            self.combo_sort_field.setCurrentText(sort_field)
            self.sort_ascending = True
            self.btn_sort_toggle.setText("Asc")

        # Refresh table (this will re-enable table sorting after populate)
        self.refresh_table()

    def export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                count = self.manager.export_to_excel(file_path)
                QMessageBox.information(self, "Success", f"Exported {count} records successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def on_table_item_changed(self, item):
        """Auto-save edited BQ fields and recalculate amount for the row and filtered total."""
        col = item.column()
        row = item.row()

        # Map editable columns to DB field names
        editable_cols = {
            1: 'Bill', 2: 'Section', 3: 'Page', 4: 'Item', 5: 'description',
            6: 'Qty', 7: 'Unit', 8: 'Rate', 9: 'Discount', 11: 'Trade', 12: 'Remark'
        }

        if col not in editable_cols:
            return

        # Get BQ ID for the row
        bq_id_item = self.table.item(row, 0)
        if not bq_id_item:
            return
        bq_id = bq_id_item.text()

        field = editable_cols[col]
        text = item.text().strip()

        # Convert numeric fields
        if field in ('Qty', 'Rate', 'Discount'):
            try:
                val = float(text) if text != '' else 0.0
            except Exception:
                QMessageBox.warning(self, "Invalid value", f"Cannot convert '{text}' to number for {field}. Reverting.")
                db_item = self.manager.get_bq_item(bq_id)
                prev = db_item.get(field, 0)
                self.table.blockSignals(True)
                self.table.setItem(row, col, QTableWidgetItem(str(prev)))
                self.table.blockSignals(False)
                return
        else:
            val = text

        # Save to DB
        try:
            self.manager.update_bq_item(bq_id, {field: val})
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save change: {e}")
            return

        # Recalculate amount for this row
        try:
            qty = float(self.table.item(row, 6).text() or 0)
        except Exception:
            qty = 0.0
        try:
            rate = float(self.table.item(row, 8).text() or 0)
        except Exception:
            rate = 0.0
        try:
            discount = float(self.table.item(row, 9).text() or 0)
        except Exception:
            discount = 0.0

        amount = qty * rate * (1 - discount)

        # Update amount cell without triggering itemChanged
        self.table.blockSignals(True)
        self.table.setItem(row, 10, QTableWidgetItem(self.format_number(amount)))
        self.table.blockSignals(False)

        # Recompute filtered total from visible rows
        total = 0.0
        for r in range(self.table.rowCount()):
            amt_item = self.table.item(r, 10)
            if not amt_item:
                continue
            try:
                amt_text = amt_item.text().replace(',', '')
                total += float(amt_text or 0)
            except Exception:
                pass
        self.label_total_amount.setText(f"Total Amount: {self.format_number(total)}")

    def add_item(self):
        # Simple add - in real app, use dialog
        bq_id = self.manager.get_next_bq_id()
        self.manager.add_bq_item(bq_id, "", "", "", "", "", 0, "", 0, 0, "", "")
        self.refresh_table()

    def delete_item(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            bq_id = self.table.item(current_row, 0).text()
            self.manager.delete_bq_item(bq_id)
            self.refresh_table()
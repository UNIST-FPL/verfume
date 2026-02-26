"""GUI test to demonstrate PSI edit mode with preview and permanent contours."""
import sys
from PyQt5.QtWidgets import QApplication
from mesh_gui_project.ui.main_window import MainWindow


def main():
    """Run GUI test showing psi edit mode."""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Load example geqdsk file
    geqdsk_path = "examples/kstar_EFIT01_35582_010000.esy_headerMod.geqdsk"
    window.load_geqdsk(geqdsk_path)

    # Switch to visualization tab
    window.left_tabs.setCurrentIndex(1)

    # Enable filled contours for better visualization
    window.psi_display_contourf_checkbox.setChecked(True)

    # Enable edit mode
    window.psi_edit_mode_button.setChecked(True)

    print("\n" + "="*70)
    print("PSI EDIT MODE TEST - INTERACTIVE DEMO")
    print("="*70)
    print("\n✅ IMPLEMENTED FEATURES:")
    print("  • PSI Edit Mode button in Visualization tab")
    print("  • Edit mode state tracking")
    print("  • Preview contour (RED DASHED) follows mouse")
    print("  • Preview updates smoothly without accumulation")
    print("  • Left-click adds permanent contour INTEGRATED with psi field")
    print("  • Added contours use SAME COLORMAP as existing visualization")
    print("  • Duplicate prevention (can't add same psi twice)")
    print("\n📋 HOW TO TEST:")
    print("  1. Move your mouse over the plot")
    print("     → Red dashed line shows preview contour")
    print("  2. Left-click to add permanent contour")
    print("     → Contour is added to the psi field visualization")
    print("     → Uses same colors/style as existing contours")
    print("  3. Move mouse to different position and click again")
    print("     → Another contour level is added")
    print("  4. Try clicking at same position")
    print("     → No duplicate (already exists)")
    print("  5. Uncheck 'Edit Psi Contours' to exit edit mode")
    print("     → Preview disappears, added contours remain")
    print("\n🎨 VISUAL GUIDE:")
    print("  • RED DASHED line = Preview (temporary, follows mouse)")
    print("  • VIRIDIS COLORMAP contours = Added + automatic levels")
    print("  • Background = Filled contours (if enabled)")
    print("\n⏭️  REMAINING WORK (not yet implemented):")
    print("  • Right-click to delete nearest contour")
    print("\n" + "="*70)
    print(f"\nAdded psi values will be shown here:")
    print(f"Current count: {len(window._added_psi_values)}")
    print("="*70 + "\n")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

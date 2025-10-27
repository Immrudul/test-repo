# test_cube_solver.py
import pytest
from solve import output_data

def test_cube_order():
    expected_edge_order = ['V', 'P', 'Q', 'C', 'K', 'E', 'I', 'G', 'H', 'W', 'X', 'N', 'T']
    expected_corner_order = ['U', 'N', 'H', 'V', 'T', 'C', 'J']

    assert output_data["edge_order"] == expected_edge_order, f"Edge order mismatch: {output_data['edge_order']}"
    assert output_data["corner_order"] == expected_corner_order, f"Corner order mismatch: {output_data['corner_order']}"

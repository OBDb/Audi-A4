import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner_by_year

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": 2017,
        "tests": [
            # Odometer
            ("7E80662295A01F4E0", {"A4_ODO": 128224.0}),
            ("7E80662295A01F515", {"A4_ODO": 128277.0}),

            # Drive time
            ("7E9056203023CB6", {"A4_DRIVE_TIME": 3885.5}),
            ("7E9056203023CBA", {"A4_DRIVE_TIME": 3886.5}),

            # Drive time (eco)
            ("7E904620303EE", {"A4_DRIVE_TIME_ECO": 95.2}),

            # Drive time (sport)
            ("7E9046203040A", {"A4_DRIVE_TIME_SPORT": 4.0}),

            # Drive time (manual)
            ("7E90462030500", {"A4_DRIVE_TIME_MANUAL": 0}),

            # Gear
            ("7E90462210F01", {"A4_GEAR": "1"}),
            ("7E90462210F03", {"A4_GEAR": "3"}),
            ("7E90462210F05", {"A4_GEAR": "5"}),
            ("7E90462210F06", {"A4_GEAR": "6"}),
            ("7E90462210F07", {"A4_GEAR": "7"}),
        ]
    },
]

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner_by_year(
                test_group['model_year'],
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}: {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])

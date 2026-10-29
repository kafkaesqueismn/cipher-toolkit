import pytest

# A few hundred letters of ordinary English. Frequency analysis needs enough
# text for the statistics to settle down -- short messages are much harder.
SAMPLE = (
    "The library was quiet in the early morning, and the only sound was the "
    "soft hum of the old radiator near the window. Students drifted in one by "
    "one, carrying coffee and heavy backpacks, and settled at the long wooden "
    "tables to study for their final examinations. Outside, the first snow of "
    "the winter was falling over the campus, covering the paths and the bare "
    "branches of the trees. Nobody seemed to notice the weather; everyone was "
    "thinking about mathematics, history, chemistry, or the essay that was due "
    "at the end of the week. When the clock struck nine, the librarian opened "
    "the reading room and the day began in earnest."
)


@pytest.fixture
def sample():
    return SAMPLE

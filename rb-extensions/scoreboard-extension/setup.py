from reviewboard.extensions.packaging import setup


PACKAGE = "scoreboard"
VERSION = "0.1"

setup(
    name=PACKAGE,
    version=VERSION,
    description="Scoreboard for Marin",
    author="None",
    packages=["scoreboard"],
    entry_points={
        'reviewboard.extensions':
            '%s = scoreboard.extension:Scoreboard' % PACKAGE,
    }
)

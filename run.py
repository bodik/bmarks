#!/usr/bin/env python3
"""zappa aws runner"""

from bmarks import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

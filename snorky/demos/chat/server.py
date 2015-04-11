# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import os
from argparse import ArgumentParser
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from snorky.service_registry import ServiceRegistry

from snorky.request_handlers.sockjs import SnorkySockJSHandler

from snorky.services.messaging import MessagingService

# Adapted from http://stackoverflow.com/a/23818878/1777162
class IndexAwareStaticFileHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return StaticFileHandler.parse_url_path(self, url_path)

if __name__ == "__main__":
    parser = ArgumentParser("demo_server")
    parser.add_argument("-p", dest="port", default=5800, type=int)
    parser.add_argument("-b", dest="do_fork", action="store_true")
    parser.add_argument("--pid-file", type=str)
    args = parser.parse_args()

    io_loop = IOLoop.instance()
    service_registry = ServiceRegistry()
    service_registry.register_service(MessagingService("messaging"))

    dirname = os.path.dirname(__file__)
    application = Application(
        SnorkySockJSHandler.get_routes(service_registry, "/sockjs") +
        [(r"/(.*)", IndexAwareStaticFileHandler, {"path": dirname})]
    )
    application.listen(args.port)
    print("Snorky running...")

    if args.do_fork:
        pid = os.fork()
        if pid > 0:
            if args.pid_file:
                with open(args.pid_file, "w") as f:
                    f.write(str(pid))
            sys.exit(0)

    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

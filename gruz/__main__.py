"""
This example demonstrates how to embed matplotlib WebAgg interactive
plotting in your own web application and framework.  It is not
necessary to do all this if you merely want to display a plot in a
browser or use matplotlib's built-in Tornado-based server "on the
side".

The framework being used must support web sockets.
"""

import io

try:
		import tornado
except ImportError:
		raise RuntimeError("This example requires tornado.")
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.websocket


from matplotlib.backends.backend_webagg_core import (
		FigureManagerWebAgg, new_figure_manager_given_figure)
from matplotlib.figure import Figure

import numpy as np

import json


def create_figure():
		"""
		Creates a simple example figure.
		"""
		fig = Figure()
		a = fig.add_subplot(111)
		t = np.arange(0.0, 3.0, 0.01)
		s = np.sin(2 * np.pi * t)
		a.plot(t, s)
		return fig


# The following is the content of the web page.  You would normally
# generate this using some sort of template facility in your web
# framework, but here we just use Python string formatting.
html_content = """

"""


class MyApplication(tornado.web.Application):
		class MainPage(tornado.web.RequestHandler):
				"""
				Serves the main HTML page.
				"""

				def get(self):
						manager = self.application.manager
						ws_uri = "ws://{req.host}/".format(req=self.request)
						# content = html_content % {
						# 		"ws_uri": ws_uri, "fig_id": manager.num}

						self.render(	"template.html",
													sock =  ws_uri,
													fig_id = manager.num
												)
						# self.write(content)

		class MplJs(tornado.web.RequestHandler):
				"""
				Serves the generated matplotlib javascript file.  The content
				is dynamically generated based on which toolbar functions the
				user has defined.  Call `FigureManagerWebAgg` to get its
				content.
				"""

				def get(self):
						self.set_header('Content-Type', 'application/javascript')
						js_content = FigureManagerWebAgg.get_javascript()

						self.write(js_content)

		class Download(tornado.web.RequestHandler):
				"""
				Handles downloading of the figure in various file formats.
				"""

				def get(self, fmt):
						manager = self.application.manager

						mimetypes = {
								'ps': 'application/postscript',
								'eps': 'application/postscript',
								'pdf': 'application/pdf',
								'svg': 'image/svg+xml',
								'png': 'image/png',
								'jpeg': 'image/jpeg',
								'tif': 'image/tiff',
								'emf': 'application/emf'
						}

						self.set_header('Content-Type', mimetypes.get(fmt, 'binary'))

						buff = io.BytesIO()
						manager.canvas.print_figure(buff, format=fmt)
						self.write(buff.getvalue())

		class WebSocket(tornado.websocket.WebSocketHandler):
				"""
				A websocket for interactive communication between the plot in
				the browser and the server.

				In addition to the methods required by tornado, it is required to
				have two callback methods:

						- ``send_json(json_content)`` is called by matplotlib when
							it needs to send json to the browser.  `json_content` is
							a JSON tree (Python dictionary), and it is the responsibility
							of this implementation to encode it as a string to send over
							the socket.

						- ``send_binary(blob)`` is called to send binary image data
							to the browser.
				"""
				supports_binary = True

				def open(self):
						# Register the websocket with the FigureManager.
						manager = self.application.manager
						manager.add_web_socket(self)
						if hasattr(self, 'set_nodelay'):
								self.set_nodelay(True)

				def on_close(self):
						# When the socket is closed, deregister the websocket with
						# the FigureManager.
						manager = self.application.manager
						manager.remove_web_socket(self)

				def on_message(self, message):
						# The 'supports_binary' message is relevant to the
						# websocket itself.  The other messages get passed along
						# to matplotlib as-is.

						# Every message has a "type" and a "figure_id".
						message = json.loads(message)
						if message['type'] == 'supports_binary':
								self.supports_binary = message['value']
						else:
								manager = self.application.manager
								manager.handle_json(message)

				def send_json(self, content):
						self.write_message(json.dumps(content))

				def send_binary(self, blob):
						if self.supports_binary:
								self.write_message(blob, binary=True)
						else:
								data_uri = "data:image/png;base64,{0}".format(
										blob.encode('base64').replace('\n', ''))
								self.write_message(data_uri)

		def __init__(self, figure):
				self.figure = figure
				self.manager = new_figure_manager_given_figure(
						id(figure), figure)

				super(MyApplication, self).__init__([
						# Static files for the CSS and JS
						(r'/_static/(.*)',
						 tornado.web.StaticFileHandler,
						 {'path': FigureManagerWebAgg.get_static_file_path()}),

						# The page that contains all of the pieces
						('/', self.MainPage),

						('/mpl.js', self.MplJs),

						# Sends images and events to the browser, and receives
						# events from the browser
						('/ws', self.WebSocket),

						# Handles the downloading (i.e., saving) of static images
						(r'/download.([a-z0-9.]+)', self.Download),
				])


if __name__ == "__main__":
		figure = create_figure()
		application = MyApplication(figure)

		http_server = tornado.httpserver.HTTPServer(application)
		http_server.listen(8080)

		print("http://127.0.0.1:8080/")
		print("Press Ctrl+C to quit")

		tornado.ioloop.IOLoop.instance().start()
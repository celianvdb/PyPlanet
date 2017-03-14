import threading
import importlib
from collections import OrderedDict

from pyplanet.apps.config import AppConfig
from pyplanet.core.exceptions import ImproperlyConfigured, InvalidAppModule
from pyplanet.god.thread import AppThread


class Apps:
	"""
	The apps class contains the context applications, loaded or not loaded in order of declaration or requirements
	if given by app configuration.

	The apps should contain a configuration class that could be loaded for reading out metadata, options and other
	useful information such as description, author, version and more.
	"""

	def __init__(self, instance):
		"""
		Initiate registry with pre-loaded apps.
		:param instance: Instance of the controller.
		:type instance: pyplanet.core.instance.Instance
		"""
		self.instance = instance

		self.apps = OrderedDict()
		self.threads = OrderedDict()

		# Set ready states.
		self.apps_ready = self.threads_ready = self.ready = False

		# Set a lock for threading.
		self._lock = threading.Lock()

	def populate(self, apps, in_order=False):
		"""
		Loads application into the apps registry. Once you populate, the order isn't yet been decided.
		After all imports are done you should shuffle the apps list so it's in the right order of execution!
		TODO: Make sure core apps are always loaded in given order.

		:param apps: Apps list.
		:type apps: list
		"""
		if self.ready:
			return

		# Load modules.
		for entry in apps:
			app = AppConfig.import_app(entry)
			thread = AppThread.create(app=app, instance=self.instance)

			# Check if the app is unique.
			if app.label in self.apps:
				raise ImproperlyConfigured('Application labels aren\'t unique! Duplicates: {}'.format(app.label))

			# Add app to list of apps.
			app.apps = self
			self.apps[app.label] = app
			self.threads[app.label] = thread

	def shuffle(self):
		# TODO
		self.ready = True
		pass

	def start(self):
		if self.apps_ready:
			raise Exception('Apps are not yet ordered!')
		if self.threads_ready:
			raise Exception('Threads of the apps are already started!')
		self.threads_ready = True

		# The apps are in order, lets loop over them.
		for label, app in self.apps.items():
			thread = self.threads[label]
			thread.start()

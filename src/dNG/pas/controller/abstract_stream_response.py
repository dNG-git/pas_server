# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;server

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasServerVersion)#
#echo(__FILEPATH__)#
"""

from collections import Iterator

from dNG.pas.data.binary import Binary
from dNG.pas.data.supports_mixin import SupportsMixin
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from dNG.pas.runtime.value_exception import ValueException

class AbstractStreamResponse(SupportsMixin):
#
	"""
A stream response reads data from a streamer and writes it to a response object.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=unused-argument

	STREAM_ITERATOR = 1
	"""
Output content directly as soon as it is available and requested by a iterator.
	"""
	STREAM_NONE = 0
	"""
Do not stream content
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractStreamResponse)

:since: v0.1.00
		"""

		SupportsMixin.__init__(self)

		self.active = True
		"""
True if ready for output.
		"""
		self.data = None
		"""
Data buffer
		"""
		self.stream_mode = 0
		"""
Stream response instead of holding it in a buffer
		"""
		self.stream_mode_supported = isinstance(self, Iterator)
		"""
Supported streaming mode
		"""
		self.streamer = None
		"""
Streamer implementation
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(AbstractStreamResponse)

:since: v0.1.00
		"""

		if (self is not None): self.finish()
	#

	def finish(self):
	#
		"""
Finish transmission and cleanup resources.

:since: v0.1.00
		"""

		if (self.active):
		#
			self.send()
			self.active = False
			self.streamer = None
		#
	#

	def is_active(self):
	#
		"""
Returns if the response stream is active.

:return: (bool) True if active
:since:  v0.1.00
		"""

		return self.active
	#

	def is_streamer_set(self):
	#
		"""
Returns true if a streamer has been set.

:return: (bool) True if set
:since:  v0.1.01
		"""

		return (self.streamer is not None)
	#

	def send(self):
	#
		"""
Send data in cache.

:since: v0.1.01
		"""

		if (self.active):
		#
			if (self.streamer is not None and self.stream_mode & AbstractStreamResponse.STREAM_ITERATOR != AbstractStreamResponse.STREAM_ITERATOR):
			#
				while (not self.streamer.is_eof()):
				#
					data = self.streamer.read()

					if (data is None): break
					else: self.send_data(data)
				#

				self.streamer.close()
				self.streamer = None
			#
			elif (self.data is not None):
			#
				self._write(self.data)
				self.data = None
			#
		#
	#

	def send_data(self, data):
	#
		"""
Sends the given data as part of the response.

:param data: Data to send

:since: v0.1.00
		"""

		if (self.active):
		#
			data = Binary.bytes(data)

			if (self.stream_mode == AbstractStreamResponse.STREAM_NONE):
			#
				if (self.data is None): self.data = Binary.BYTES_TYPE()
				self.data += data
			#
			else: self._write(data)
		#
	#

	def set_active(self, is_active = True):
	#
		"""
Sets the stream response active.

:param is_active: True if active

:since: v0.1.00
		"""

		self.active = is_active
		if (not is_active): self.data = None
	#

	def set_streamer(self, streamer):
	#
		"""
Sets the streamer to create response data when requested.

:since: v0.1.01
		"""

		# pylint: disable=no-member

		if (not hasattr(streamer, "read")): raise ValueException("Given streaming object is not supported.")
		self.streamer = streamer

		if (self.stream_mode_supported & AbstractStreamResponse.STREAM_ITERATOR == AbstractStreamResponse.STREAM_ITERATOR): self.stream_mode |= AbstractStreamResponse.STREAM_ITERATOR
		if (self.is_supported("streaming")): self.set_stream_mode()
	#

	def _write(self, data):
	#
		"""
Writes the given data.

:param data: Data to be send

:since: v0.1.00
		"""

		raise NotImplementedException()
	#
#

##j## EOF
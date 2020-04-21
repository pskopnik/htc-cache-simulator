from typing import Dict, List, Sequence

from ..workload import BytesSize, FileID, PartInd, PartSpec


class InsufficientFreeSpace(Exception):
	pass


class Storage(object):
	def __init__(self, total_bytes: BytesSize):
		self._total_bytes: BytesSize = total_bytes
		self._used_bytes: BytesSize = 0
		self._files: Dict[FileID, Dict[PartInd, BytesSize]] = {}

	@property
	def total_bytes(self) -> BytesSize:
		return self._total_bytes

	@property
	def used_bytes(self) -> BytesSize:
		return self._used_bytes

	@property
	def free_bytes(self) -> BytesSize:
		return self._total_bytes - self._used_bytes

	def parts(self, file: FileID) -> List[PartSpec]:
		"""Returns all parts of file which are contained in the storage.
		"""
		try:
			file_parts = self._files[file]
		except KeyError:
			return []

		return sorted((part_ind, part_bytes) for part_ind, part_bytes in file_parts.items())

	def contains_file(self, file: FileID) -> bool:
		return file in self._files

	def contains(self, file: FileID, parts: Sequence[PartSpec]) -> bool:
		try:
			file_parts = self._files[file]
		except KeyError:
			return False

		for part_ind, part_bytes in parts:
			if file_parts.get(part_ind, 0) < part_bytes:
				return False

		return True

	def contained_bytes(self, file: FileID, parts: Sequence[PartSpec]) -> BytesSize:
		try:
			file_parts = self._files[file]
		except KeyError:
			return 0

		return sum(
			min(file_parts.get(part_ind, 0), part_bytes) for part_ind, part_bytes in parts
		)

	def missing_bytes(self, file: FileID, parts: Sequence[PartSpec]) -> BytesSize:
		requested_bytes = sum(part_bytes for part_ind, part_bytes in parts)

		return requested_bytes - self.contained_bytes(file, parts)

	def evict(self, file: FileID) -> BytesSize:
		"""Evicts all parts of file from the storage.

		Returns:
			Number of bytes evicted from the storage.
		"""
		try:
			file_parts = self._files[file]
		except KeyError:
			return 0

		del self._files[file]

		evicted_bytes = sum(file_parts.values())
		self._used_bytes -= evicted_bytes

		return evicted_bytes


	def place(self, file: FileID, parts: Sequence[PartSpec]) -> BytesSize:
		"""Places the passed parts of file in the storage.

		Returns:
			Number of bytes added to the storage.
		"""
		missing_bytes = self.missing_bytes(file, parts)
		if self.free_bytes < missing_bytes:
			raise InsufficientFreeSpace()

		try:
			file_parts = self._files[file]
		except KeyError:
			file_parts = {}
			self._files[file] = file_parts

		for part_ind, part_bytes in parts:
			file_parts[part_ind] = max(file_parts.get(part_ind, 0), part_bytes)

		self._used_bytes += missing_bytes

		return missing_bytes

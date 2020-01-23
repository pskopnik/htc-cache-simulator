from ..processor import AccessInfo, Access
from ..state import FileID, StateDrivenProcessor, StateDrivenOnlineProcessor
from typing import Iterable, List, Optional, Set
import random


class Rand(StateDrivenOnlineProcessor):
	"""Processor evicting a random file from the cache.
	"""

	class State(StateDrivenProcessor.State):
		class Item(StateDrivenProcessor.State.Item):
			def __init__(self, state: 'Rand.State', ind: int):
				self._state: Rand.State = state
				self._ind: int = ind

			@property
			def file(self) -> FileID:
				return self._state._files[self._ind]

		def __init__(self) -> None:
			self._files: List[FileID] = []
			self._files_set: Set[FileID] = set()

		def pop_eviction_candidates(
			self,
			file: FileID = "",
			ind: int = 0,
			requested_bytes: int = 0,
			contained_bytes: int = 0,
			missing_bytes: int = 0,
			free_bytes: int = 0,
			required_bytes: int = 0,
		) -> Iterable[FileID]:
			ind = random.randrange(len(self._files))
			file = self._files[ind]
			self._files[ind] = self._files[-1]
			self._files.pop()
			self._files_set.remove(file)
			return (file,)

		def find(self, file: FileID) -> Optional[Item]:
			try:
				ind = self._files.index(file)
				return Rand.State.Item(self, ind)
			except ValueError:
				return None

		def remove(self, item: StateDrivenProcessor.State.Item) -> None:
			if not isinstance(item, Rand.State.Item):
				raise TypeError("unsupported item type passed")

			del self._files[item._ind]

		def remove_file(self, file: FileID) -> None:
			self._files.remove(file)

		def process_access(
			self,
			file: FileID,
			ind: int = 0,
			ensure: bool = True,
			requested_bytes: int = 0,
			placed_bytes: int = 0,
			total_bytes: int = 0,
		) -> None:
			if not ensure or file not in self._files_set:
				self._files.append(file)
				self._files_set.add(file)

	def _init_state(self) -> 'Rand.State':
		return Rand.State()

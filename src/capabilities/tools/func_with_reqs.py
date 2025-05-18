from __future__ import annotations

import functools
import inspect
from dataclasses import dataclass, field
from importlib.abc import SourceLoader
from importlib.util import module_from_spec, spec_from_loader
from textwrap import dedent, indent
from typing import Any, Callable, Generic, List, Sequence, Set, Tuple, TypeVar, Union

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


def _to_code(func: Union[FunctionWithRequirements[T, P], Callable[P, T], FunctionWithRequirementsStr]) -> str:
    if isinstance(func, FunctionWithRequirementsStr):
        return func.func

    if isinstance(func, FunctionWithRequirements):
        code = inspect.getsource(func.func)
    else:
        code = inspect.getsource(func)
    # Strip the decorator
    if code.startswith("@"):
        code = code[code.index("\n") + 1 :]
    return code


@dataclass(frozen=True)
class Alias:
    name: str
    alias: str


@dataclass(frozen=True)
class ImportFromModule:
    module: str
    imports: Tuple[Union[str, Alias], ...]

    # backward compatibility
    def __init__(
        self,
        module: str,
        imports: Union[Tuple[Union[str, Alias], ...], List[Union[str, Alias]]],
    ):
        object.__setattr__(self, "module", module)
        if isinstance(imports, list):
            object.__setattr__(self, "imports", tuple(imports))
        else:
            object.__setattr__(self, "imports", imports)


Import = Union[str, ImportFromModule, Alias]


def _import_to_str(im: Import) -> str:
    if isinstance(im, str):
        return f"import {im}"
    elif isinstance(im, Alias):
        return f"import {im.name} as {im.alias}"
    else:

        def to_str(i: Union[str, Alias]) -> str:
            if isinstance(i, str):
                return i
            else:
                return f"{i.name} as {i.alias}"

        imports = ", ".join(map(to_str, im.imports))
        return f"from {im.module} import {imports}"


class _StringLoader(SourceLoader):
    def __init__(self, data: str):
        self.data = data

    def get_source(self, fullname: str) -> str:
        return self.data

    def get_data(self, path: str) -> bytes:
        return self.data.encode("utf-8")

    def get_filename(self, fullname: str) -> str:
        return "<not a real path>/" + fullname + ".py"


@dataclass
class FunctionWithRequirementsStr:
    func: str
    compiled_func: Callable[..., Any]
    _func_name: str
    python_packages: Sequence[str] = field(default_factory=list)
    global_imports: Sequence[Import] = field(default_factory=list)

    def __init__(self, func: str, python_packages: Sequence[str] = [], global_imports: Sequence[Import] = []):
        self.func = func
        self.python_packages = python_packages
        self.global_imports = global_imports

        module_name = "func_module"
        loader = _StringLoader(func)
        spec = spec_from_loader(module_name, loader)
        if spec is None:
            raise ValueError("Could not create spec")
        module = module_from_spec(spec)
        if spec.loader is None:
            raise ValueError("Could not create loader")

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            raise ValueError(f"Could not compile function: {e}") from e

        functions = inspect.getmembers(module, inspect.isfunction)
        if len(functions) != 1:
            raise ValueError("The string must contain exactly one function")

        self._func_name, self.compiled_func = functions[0]

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError("String based function with requirement objects are not directly callable")


@dataclass
class FunctionWithRequirements(Generic[T, P]):
    func: Callable[P, T]
    python_packages: Sequence[str] = field(default_factory=list)
    global_imports: Sequence[Import] = field(default_factory=list)

    @classmethod
    def from_callable(
        cls, func: Callable[P, T], python_packages: Sequence[str] = [], global_imports: Sequence[Import] = []
    ) -> FunctionWithRequirements[T, P]:
        return cls(python_packages=python_packages, global_imports=global_imports, func=func)

    @staticmethod
    def from_str(
        func: str, python_packages: Sequence[str] = [], global_imports: Sequence[Import] = []
    ) -> FunctionWithRequirementsStr:
        return FunctionWithRequirementsStr(func=func, python_packages=python_packages, global_imports=global_imports)

    # Type this based on F
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.func(*args, **kwargs)

def to_code(func: Union[FunctionWithRequirements[T, P], Callable[P, T], FunctionWithRequirementsStr]) -> str:
    return _to_code(func)


def import_to_str(im: Import) -> str:
    return _import_to_str(im)

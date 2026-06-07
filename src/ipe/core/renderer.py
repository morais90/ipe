import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from jinja2 import ChoiceLoader, Environment, FileSystemLoader

from ipe.targets.base import LanguageTarget

_REPEATED_PATTERN = re.compile(r"\{(\w+)\}")
_HTML_LINK = re.compile(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>')
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
_BLANK_LINES = re.compile(r"\n\s*\n\s*\n")

_SINGULAR: dict[str, str] = {
    "models": "model",
    "resources": "resource",
    "requests": "model",
}


class TemplateTreeRenderer:
    def __init__(self, target: LanguageTarget) -> None:
        self._target = target
        self._env: Environment | None = None

    def render(
        self,
        template_dir: Path,
        output_dir: Path,
        context: dict[str, Any],
        custom_dir: Path | None = None,
        on_file: Callable[[Path], None] | None = None,
    ) -> list[Path]:
        env = self._get_env(template_dir, custom_dir)
        written: list[Path] = []

        for template_path in sorted(template_dir.rglob("*.jinja")):
            relative = template_path.relative_to(template_dir)
            new_files = self._process_template(env, relative, output_dir, context)
            written.extend(new_files)
            if on_file:
                for path in new_files:
                    on_file(path)

        return written

    def _get_env(self, template_dir: Path, custom_dir: Path | None) -> Environment:
        if self._env is not None:
            return self._env

        loaders = []
        if custom_dir is not None:
            loaders.append(FileSystemLoader(str(custom_dir)))
        loaders.append(FileSystemLoader(str(template_dir)))

        env = Environment(
            loader=ChoiceLoader(loaders) if custom_dir else loaders[0],
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        env.filters["strip_html"] = _strip_html

        naming = self._target.naming
        env.filters["class_name"] = naming.class_name
        env.filters["method_name"] = naming.method_name
        env.filters["field_name"] = naming.field_name
        env.filters["module_name"] = naming.module_name

        for name, func in self._target.filters().items():
            env.filters[name] = func

        self._env = env
        return env

    def _process_template(
        self,
        env: Environment,
        relative: Path,
        output_dir: Path,
        context: dict[str, Any],
    ) -> list[Path]:
        match = _REPEATED_PATTERN.search(relative.stem)

        if match:
            return self._render_repeated(env, relative, output_dir, context, match)
        return self._render_single(env, relative, output_dir, context)

    def _render_single(
        self,
        env: Environment,
        relative: Path,
        output_dir: Path,
        context: dict[str, Any],
    ) -> list[Path]:
        output_path = output_dir / _strip_jinja(relative)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        template = env.get_template(str(relative))
        content = template.render(context)
        output_path.write_text(content, encoding="utf-8")

        return [output_path]

    def _render_repeated(
        self,
        env: Environment,
        relative: Path,
        output_dir: Path,
        context: dict[str, Any],
        match: re.Match[str],
    ) -> list[Path]:
        attr_name = match.group(1)
        collection_key = relative.parent.name
        singular_key = _SINGULAR.get(collection_key, collection_key)
        collection = context.get(collection_key, {})
        template = env.get_template(str(relative))
        written: list[Path] = []

        items = (
            collection.items()
            if isinstance(collection, dict)
            else enumerate(collection)
        )

        for key, item in items:
            if isinstance(item, dict):
                item_name = self._target.naming.module_name(
                    item.get(attr_name, str(key))
                )
            else:
                item_name = self._target.naming.module_name(str(key))

            output_path = output_dir / relative.parent / f"{item_name}.py"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            item_context = {
                **context,
                singular_key: item,
                "item_name": item_name,
                "item_key": key,
                "operations": item if isinstance(item, list) else [],
            }

            content = template.render(item_context)
            output_path.write_text(content, encoding="utf-8")
            written.append(output_path)

        return written


def _strip_jinja(path: Path) -> Path:
    return path.with_name(path.name.removesuffix(".jinja"))


def _strip_html(text: str) -> str:
    text = _HTML_LINK.sub(r"\2", text)
    text = _HTML_TAG.sub("", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent / ".packages"
PYWIN32_DLLS = PACKAGE_ROOT / "pywin32_system32"
if PYWIN32_DLLS.exists():
    sys.path.insert(0, str(PACKAGE_ROOT))
    for directory in (
        PACKAGE_ROOT / "win32",
        PACKAGE_ROOT / "win32" / "lib",
        PACKAGE_ROOT / "pythonwin",
        PYWIN32_DLLS,
    ):
        sys.path.insert(0, str(directory))
    os.add_dll_directory(str(PYWIN32_DLLS))

import pythoncom
import win32com.client


def export_docx(source: Path, destination: Path) -> int:
    source = source.resolve()
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    pythoncom.CoInitialize()
    word = None
    document = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        word.AutomationSecurity = 3
        word.Options.SaveNormalPrompt = False
        word.Options.UpdateLinksAtOpen = False
        document = word.Documents.Open(
            str(source),
            ConfirmConversions=False,
            ReadOnly=True,
            AddToRecentFiles=False,
            Visible=False,
            OpenAndRepair=True,
            NoEncodingDialog=True,
        )
        document.Repaginate()
        pages = int(document.ComputeStatistics(2))
        document.ExportAsFixedFormat(
            OutputFileName=str(destination),
            ExportFormat=17,
            OpenAfterExport=False,
            OptimizeFor=0,
            Range=0,
            Item=0,
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
        )
        return pages
    finally:
        if document is not None:
            document.Close(False)
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    pages = export_docx(args.source, args.destination)
    print(f"WordPages={pages}")
    print(args.destination.resolve())


if __name__ == "__main__":
    main()

"""WebClone v2.0 Paketleme ve Derleme Aracı.

Kullanım:
  python build.py            # Wheel ve Source paketlerini derler (dist/ klasörüne)
  python build.py --clean    # Önbellek ve geçici dosyaları temizler
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def clean() -> None:
    print("🧹 Temizlik yapılıyor...")
    patterns = ["build", "dist", "*.egg-info", "__pycache__", ".pytest_cache"]
    for pattern in patterns:
        for p in BASE_DIR.glob(pattern):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                print(f"  Silindi: {p.relative_to(BASE_DIR)}")
            elif p.is_file():
                p.unlink()
                print(f"  Silindi: {p.relative_to(BASE_DIR)}")

    for pyc in BASE_DIR.rglob("*.pyc"):
        pyc.unlink(missing_ok=True)


def build_package() -> None:
    clean()
    print("\n📦 Python Wheel ve Kaynak Paketi Derleniyor...")
    cmd = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
    res = subprocess.run(cmd, cwd=BASE_DIR, check=False)
    if res.returncode == 0:
        print("\n✅ Derleme tamamlandı! Paketler:")
        dist_dir = BASE_DIR / "dist"
        if dist_dir.exists():
            for f in dist_dir.glob("*"):
                size_kb = f.stat().st_size / 1024
                print(f"   • {f.name} ({size_kb:.1f} KB)")
    else:
        print("\n❌ Derleme sırasında hata oluştu.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        clean()
    else:
        build_package()

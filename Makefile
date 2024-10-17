PREFIX ?= ~/.local
VENV_DIR = $(PREFIX)/yt-dlp-sc
BINDIR ?= $(PREFIX)/bin
PYTHON = $(VENV_DIR)/bin/python3
PIP = ${VENV_DIR}/bin/pip

# Targets
.PHONY: all install clean

.DEFAULT_GOAL = help

help:
	@echo "---------------HELP-----------------"
	@echo "make install   - Installs the project"
	@echo "make uninstall - Uninstalls the project"
	@echo "make test      - Runs tests"
	@echo "make clean     - Cleans the pycache"
	@echo "------------------------------------"

all: install

setup: requirements.txt
	@python3 -m venv ${VENV_DIR}
	@pip install -r requirements.txt

install: requirements.txt
	@echo "Creating virtual environment"
	@python3 -m venv $(VENV_DIR)
	@echo "Installing dependencies"
	@${PIP} install -r requirements.txt
	@echo "Installing yt-dlp-sc.py"
	@mkdir -p ~/.config/yt-dlp-sc
	@install -m 644 options.conf ~/.config/yt-dlp-sc/options.conf
	@install -m 755 yt-dlp-sc.py $(BINDIR)/yt-dlp-sc
	@chmod +x $(BINDIR)/yt-dlp-sc
	@echo "yt-dlp-sc installed to $(BINDIR)/yt-dlp-sc"
	@echo "Installation successful. Run 'yt-dlp-sc' to begin."

run: venv/bin/activate
	@${VENV_DIR}/bin/python yt-dlp-sc.py

venv/bin/activate: requirements.txt
	@${PYTHON} -m venv ${VENV_DIR}
	@${PIP} install -r requirements.txt

uninstall:
	@echo "Uninstalling"
	@rm -f $(BINDIR)/yt-dlp-sc
	@echo "Uninstalled yt-dlp-sc."

clean:
	@rm -rf ${VENV_DIR}
	@echo "Remove venv directory"

test:
	@${PYTHON} --version
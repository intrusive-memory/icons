CATALOG := Sources/Icons/Resources/Icons.xcassets
BUILD   := build
BUNDLE  := $(BUILD)/Preview.bundle
SYMBOLS  = $(patsubst $(CATALOG)/%.symbolset,%,$(wildcard $(CATALOG)/*.symbolset))

.PHONY: help generate validate preview build test clean

help: ## List targets
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

generate: ## Regenerate script-built symbols into the asset catalog
	python3 Scripts/generate-storyboard-symbols.py

validate: ## Compile the asset catalog with actool; fails on any warning or error
	@mkdir -p $(BUNDLE)/Contents/Resources
	@printf '<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>CFBundleIdentifier</key><string>icons.preview</string><key>CFBundlePackageType</key><string>BNDL</string></dict></plist>' > $(BUNDLE)/Contents/Info.plist
	@xcrun actool $(CATALOG) --compile $(BUNDLE)/Contents/Resources --platform macosx \
		--minimum-deployment-target 14.0 --output-format human-readable-text --warnings --errors \
		> $(BUILD)/actool.log 2>&1
	@if grep -qiE 'warning|error' $(BUILD)/actool.log; then cat $(BUILD)/actool.log; exit 1; fi
	@echo "actool: $(words $(SYMBOLS)) symbols OK"

preview: validate ## Render every symbol to build/preview.png and open it
	@xcrun swiftc -O Scripts/preview.swift -o $(BUILD)/preview
	@$(BUILD)/preview $(BUNDLE) $(BUILD)/preview.png $(SYMBOLS)
	@open -a Preview $(BUILD)/preview.png

build: ## Build the package for macOS
	xcodebuild build -scheme Icons -destination 'platform=macOS,arch=arm64,variant=macos' -quiet

test: ## Run the package tests on macOS
	xcodebuild test -scheme Icons -destination 'platform=macOS,arch=arm64,variant=macos' -quiet

clean: ## Remove build output
	rm -rf $(BUILD)

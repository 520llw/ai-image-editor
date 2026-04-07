#!/bin/bash
# AI Image Editor - Frontend Testing Script
# Tests frontend project structure, dependencies, and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Frontend directory
FRONTEND_DIR="/mnt/okcomputer/output/frontend"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    ((TESTS_TOTAL++))
    
    echo -e "\n${BLUE}=== Testing: $test_name ===${NC}"
    if eval "$test_cmd"; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name"
        return 1
    fi
}

check_file_exists() {
    local file="$1"
    local description="$2"
    if [ -f "$file" ]; then
        log_pass "$description exists: $file"
        return 0
    else
        log_fail "$description missing: $file"
        return 1
    fi
}

check_dir_exists() {
    local dir="$1"
    local description="$2"
    if [ -d "$dir" ]; then
        log_pass "$description exists: $dir"
        return 0
    else
        log_fail "$description missing: $dir"
        return 1
    fi
}

# ==================== TEST SUITE ====================

echo "========================================"
echo "  AI Image Editor - Frontend Tests"
echo "========================================"
echo ""

# Test 1: Project Structure
echo -e "\n${BLUE}=== TEST GROUP: Project Structure ===${NC}"

check_dir_exists "$FRONTEND_DIR" "Frontend directory"
check_dir_exists "$FRONTEND_DIR/src" "Source directory"
check_dir_exists "$FRONTEND_DIR/src/components" "Components directory"
check_dir_exists "$FRONTEND_DIR/src/api" "API directory"
check_dir_exists "$FRONTEND_DIR/src/types" "Types directory"
check_dir_exists "$FRONTEND_DIR/src/stores" "Stores directory"
check_dir_exists "$FRONTEND_DIR/src/hooks" "Hooks directory"

# Test 2: Configuration Files
echo -e "\n${BLUE}=== TEST GROUP: Configuration Files ===${NC}"

check_file_exists "$FRONTEND_DIR/package.json" "package.json"
check_file_exists "$FRONTEND_DIR/tsconfig.json" "tsconfig.json"
check_file_exists "$FRONTEND_DIR/vite.config.ts" "vite.config.ts"
check_file_exists "$FRONTEND_DIR/tailwind.config.js" "tailwind.config.js"
check_file_exists "$FRONTEND_DIR/postcss.config.js" "postcss.config.js"

# Test 3: Source Files
echo -e "\n${BLUE}=== TEST GROUP: Source Files ===${NC}"

check_file_exists "$FRONTEND_DIR/src/main.tsx" "main.tsx"
check_file_exists "$FRONTEND_DIR/src/App.tsx" "App.tsx"
check_file_exists "$FRONTEND_DIR/src/api/client.ts" "API client"
check_file_exists "$FRONTEND_DIR/src/api/imageApi.ts" "Image API"
check_file_exists "$FRONTEND_DIR/src/types/index.ts" "Type definitions"
check_file_exists "$FRONTEND_DIR/src/stores/editorStore.ts" "Editor store"

# Test 4: Component Files
echo -e "\n${BLUE}=== TEST GROUP: Component Files ===${NC}"

# UI Components
check_file_exists "$FRONTEND_DIR/src/components/ui/button.tsx" "Button component"
check_file_exists "$FRONTEND_DIR/src/components/ui/card.tsx" "Card component"
check_file_exists "$FRONTEND_DIR/src/components/ui/input.tsx" "Input component"
check_file_exists "$FRONTEND_DIR/src/components/ui/slider.tsx" "Slider component"
check_file_exists "$FRONTEND_DIR/src/components/ui/select.tsx" "Select component"
check_file_exists "$FRONTEND_DIR/src/components/ui/progress.tsx" "Progress component"
check_file_exists "$FRONTEND_DIR/src/components/ui/alert.tsx" "Alert component"
check_file_exists "$FRONTEND_DIR/src/components/ui/toast.tsx" "Toast component"

# Image Components
check_file_exists "$FRONTEND_DIR/src/components/image/ImageUploader.tsx" "ImageUploader component"
check_file_exists "$FRONTEND_DIR/src/components/image/ImagePreview.tsx" "ImagePreview component"
check_file_exists "$FRONTEND_DIR/src/components/image/ImageComparison.tsx" "ImageComparison component"

# Editor Components
check_file_exists "$FRONTEND_DIR/src/components/editor/PromptInput.tsx" "PromptInput component"
check_file_exists "$FRONTEND_DIR/src/components/editor/StyleSelector.tsx" "StyleSelector component"
check_file_exists "$FRONTEND_DIR/src/components/editor/StrengthSlider.tsx" "StrengthSlider component"
check_file_exists "$FRONTEND_DIR/src/components/editor/StepsSlider.tsx" "StepsSlider component"
check_file_exists "$FRONTEND_DIR/src/components/editor/GenerateButton.tsx" "GenerateButton component"

# Layout Components
check_file_exists "$FRONTEND_DIR/src/components/layout/Header.tsx" "Header component"

# Test 5: Package.json Validation
echo -e "\n${BLUE}=== TEST GROUP: Package.json Validation ===${NC}"

if [ -f "$FRONTEND_DIR/package.json" ]; then
    # Check for required dependencies
    if grep -q '"react"' "$FRONTEND_DIR/package.json"; then
        log_pass "React dependency found"
    else
        log_fail "React dependency missing"
    fi
    
    if grep -q '"axios"' "$FRONTEND_DIR/package.json"; then
        log_pass "Axios dependency found"
    else
        log_fail "Axios dependency missing"
    fi
    
    if grep -q '"zustand"' "$FRONTEND_DIR/package.json"; then
        log_pass "Zustand dependency found"
    else
        log_fail "Zustand dependency missing"
    fi
    
    if grep -q '"tailwindcss"' "$FRONTEND_DIR/package.json"; then
        log_pass "TailwindCSS dependency found"
    else
        log_fail "TailwindCSS dependency missing"
    fi
    
    if grep -q '"typescript"' "$FRONTEND_DIR/package.json"; then
        log_pass "TypeScript dependency found"
    else
        log_fail "TypeScript dependency missing"
    fi
    
    if grep -q '"vite"' "$FRONTEND_DIR/package.json"; then
        log_pass "Vite dependency found"
    else
        log_fail "Vite dependency missing"
    fi
    
    # Check for required scripts
    if grep -q '"dev"' "$FRONTEND_DIR/package.json"; then
        log_pass "dev script found"
    else
        log_fail "dev script missing"
    fi
    
    if grep -q '"build"' "$FRONTEND_DIR/package.json"; then
        log_pass "build script found"
    else
        log_fail "build script missing"
    fi
else
    log_fail "package.json not found"
fi

# Test 6: TypeScript Configuration
echo -e "\n${BLUE}=== TEST GROUP: TypeScript Configuration ===${NC}"

if [ -f "$FRONTEND_DIR/tsconfig.json" ]; then
    if grep -q '"strict": true' "$FRONTEND_DIR/tsconfig.json"; then
        log_pass "TypeScript strict mode enabled"
    else
        log_warn "TypeScript strict mode not enabled"
    fi
    
    if grep -q '"paths"' "$FRONTEND_DIR/tsconfig.json"; then
        log_pass "Path aliases configured"
    else
        log_fail "Path aliases not configured"
    fi
    
    if grep -q '"jsx": "react-jsx"' "$FRONTEND_DIR/tsconfig.json"; then
        log_pass "JSX transform configured"
    else
        log_warn "JSX transform not configured"
    fi
else
    log_fail "tsconfig.json not found"
fi

# Test 7: Vite Configuration
echo -e "\n${BLUE}=== TEST GROUP: Vite Configuration ===${NC}"

if [ -f "$FRONTEND_DIR/vite.config.ts" ]; then
    if grep -q "@vitejs/plugin-react" "$FRONTEND_DIR/vite.config.ts"; then
        log_pass "React plugin configured"
    else
        log_fail "React plugin not configured"
    fi
    
    if grep -q "proxy" "$FRONTEND_DIR/vite.config.ts"; then
        log_pass "API proxy configured"
    else
        log_warn "API proxy not configured"
    fi
    
    if grep -q "'@'" "$FRONTEND_DIR/vite.config.ts"; then
        log_pass "Path alias configured in Vite"
    else
        log_fail "Path alias not configured in Vite"
    fi
else
    log_fail "vite.config.ts not found"
fi

# Test 8: API Client Configuration
echo -e "\n${BLUE}=== TEST GROUP: API Client Configuration ===${NC}"

if [ -f "$FRONTEND_DIR/src/api/client.ts" ]; then
    if grep -q "axios.create" "$FRONTEND_DIR/src/api/client.ts"; then
        log_pass "Axios instance created"
    else
        log_fail "Axios instance not created"
    fi
    
    if grep -q "baseURL" "$FRONTEND_DIR/src/api/client.ts"; then
        log_pass "Base URL configured"
    else
        log_fail "Base URL not configured"
    fi
    
    if grep -q "interceptors" "$FRONTEND_DIR/src/api/client.ts"; then
        log_pass "Request/Response interceptors configured"
    else
        log_warn "Interceptors not configured"
    fi
    
    if grep -q "multipart/form-data" "$FRONTEND_DIR/src/api/client.ts"; then
        log_pass "Form data support configured"
    else
        log_warn "Form data support not configured"
    fi
else
    log_fail "API client not found"
fi

# Test 9: Type Definitions
echo -e "\n${BLUE}=== TEST GROUP: Type Definitions ===${NC}"

if [ -f "$FRONTEND_DIR/src/types/index.ts" ]; then
    if grep -q "UploadedImage" "$FRONTEND_DIR/src/types/index.ts"; then
        log_pass "UploadedImage type defined"
    else
        log_fail "UploadedImage type not defined"
    fi
    
    if grep -q "GenerationParams" "$FRONTEND_DIR/src/types/index.ts"; then
        log_pass "GenerationParams type defined"
    else
        log_fail "GenerationParams type not defined"
    fi
    
    if grep -q "GenerationTask" "$FRONTEND_DIR/src/types/index.ts"; then
        log_pass "GenerationTask type defined"
    else
        log_fail "GenerationTask type not defined"
    fi
    
    if grep -q "EditorState" "$FRONTEND_DIR/src/types/index.ts"; then
        log_pass "EditorState type defined"
    else
        log_fail "EditorState type not defined"
    fi
else
    log_fail "Type definitions not found"
fi

# Test 10: Store Configuration
echo -e "\n${BLUE}=== TEST GROUP: Store Configuration ===${NC}"

if [ -f "$FRONTEND_DIR/src/stores/editorStore.ts" ]; then
    if grep -q "zustand" "$FRONTEND_DIR/src/stores/editorStore.ts"; then
        log_pass "Zustand store configured"
    else
        log_fail "Zustand store not configured"
    fi
    
    if grep -q "persist" "$FRONTEND_DIR/src/stores/editorStore.ts"; then
        log_pass "Store persistence configured"
    else
        log_warn "Store persistence not configured"
    fi
else
    log_fail "Editor store not found"
fi

# Test 11: Image API Functions
echo -e "\n${BLUE}=== TEST GROUP: Image API Functions ===${NC}"

if [ -f "$FRONTEND_DIR/src/api/imageApi.ts" ]; then
    if grep -q "uploadImage" "$FRONTEND_DIR/src/api/imageApi.ts"; then
        log_pass "uploadImage function defined"
    else
        log_fail "uploadImage function not defined"
    fi
    
    if grep -q "generateImage" "$FRONTEND_DIR/src/api/imageApi.ts"; then
        log_pass "generateImage function defined"
    else
        log_fail "generateImage function not defined"
    fi
    
    if grep -q "getTaskStatus" "$FRONTEND_DIR/src/api/imageApi.ts"; then
        log_pass "getTaskStatus function defined"
    else
        log_fail "getTaskStatus function not defined"
    fi
    
    if grep -q "pollTaskStatus" "$FRONTEND_DIR/src/api/imageApi.ts"; then
        log_pass "pollTaskStatus function defined"
    else
        log_fail "pollTaskStatus function not defined"
    fi
    
    if grep -q "validateImageFile" "$FRONTEND_DIR/src/api/imageApi.ts"; then
        log_pass "validateImageFile function defined"
    else
        log_fail "validateImageFile function not defined"
    fi
else
    log_fail "Image API not found"
fi

# Test 12: Tailwind Configuration
echo -e "\n${BLUE}=== TEST GROUP: Tailwind Configuration ===${NC}"

if [ -f "$FRONTEND_DIR/tailwind.config.js" ]; then
    if grep -q "content" "$FRONTEND_DIR/tailwind.config.js"; then
        log_pass "Tailwind content paths configured"
    else
        log_fail "Tailwind content paths not configured"
    fi
    
    if grep -q "theme" "$FRONTEND_DIR/tailwind.config.js"; then
        log_pass "Tailwind theme configured"
    else
        log_warn "Tailwind theme not configured"
    fi
else
    log_fail "tailwind.config.js not found"
fi

# ==================== SUMMARY ====================

echo ""
echo "========================================"
echo "           TEST SUMMARY"
echo "========================================"
echo -e "Total Tests:  $TESTS_TOTAL"
echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed!${NC}"
    exit 1
fi

# qr_python
QR Code Generation in Python


## TODO

List of components to build
- [ ] Input Handling
- [x] Grid to Image
- [x] QR Element Placement
- [x] Data Encoding
- [x] Data Placement
- [x] Function Patterns
- [x] Mask Patterns
- [x] Error Correction
- [x] Mask Evaluation and Scoring

# Refactor
Challenge: How do I make sure that the error correction and the data interleaving cooperate?

## Data Flow
1. Data input
2. Encoding analysis
3. Version and ECC level picking
4. Error Correction Coding
5. QR Assembly
  - Pattern placement
  - Data placement
  - Masking
  - Metadata placement
6. Grid -> Image

## Components
1. Reed-Solomon Coding Component  (Doesn't Need refactor)
2. Data encoders                  (Doesn't Need refactor)
3. Grid -> Image Component        (Doesn't Need refactor)
4. QR Assembly component          (Full Redesign)

Ideally the QR Assembly is split into several smaller components because at the moment it's an enormous block of code which is opaque and hard to work with.

## Possible Solutions?
- Create a grid component which manages the grid operations such as setting modules etc. It should manage it's own state, be copyable, etc.

Additionally; aggressively clean out dead code.

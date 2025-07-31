# Jack Compiler

## Overview

This repository contains a compiler for the Jack programming language, as described in the book _The Elements of Computing Systems_ (Nand2Tetris). The Jack Compiler translates high-level Jack code into Virtual Machine (VM) code that can be executed on the Hack computer platform.

## Features

- **Lexical Analysis**: Tokenizes Jack source code into meaningful components.
- **Syntax Analysis**: Parses tokens to ensure they conform to Jack's grammar rules.
- **Code Generation**: Produces VM code compatible with the Hack Virtual Machine.

## Prerequisites

To use this compiler, ensure you have the following:

- Python 3.6 or higher
- Nand2Tetris software suite (for testing the generated VM code)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Levan-Demetrashvili/jack-compiler.git
   ```
2. Navigate to the project directory:
   ```bash
   cd jack-compiler
   ```

## Usage

To compile a Jack file or directory containing Jack files:

```bash
python JackCompiler.py <path-to-jack-file-or-directory>
```

- **Single File**: Provide the path to a `.jack` file to compile it into a `.vm` file.
- **Directory**: Provide a directory path to compile all `.jack` files within it into corresponding `.vm` files.

Example:

```bash
python JackCompiler.py ./Pong
```

Output files will be generated in the same directory as the input files, with a `.vm` extension.

## Testing

To test the compiler, use the Nand2Tetris VM Emulator to run the generated `.vm` files.

1. Compile a Jack program:
   ```bash
   python JackCompiler.py ./Pong
   ```
2. Load the generated `.vm` files into the VM Emulator.
3. Run the program to verify correct behavior.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Open a pull request.

## Acknowledgments

- Inspired by the Nand2Tetris course and _The Elements of Computing Systems_ by Noam Nisan and Shimon Schocken.

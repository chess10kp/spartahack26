{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python310
    gcc                   # or gcc-unwrapped — provides libstdc++.so.6
    # optional but often helpful for OpenCV / numpy / scipy stack:
    stdenv.cc.cc.lib
    zlib
    libGL
  ];

shellHook = ''
  unset LD_LIBRARY_PATH  # optional: clears any inherited junk that might conflict

  export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc.lib
    # add more if you later need them, e.g.:
    # pkgs.zlib
    # pkgs.libGL
  ]}''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}

  echo "Nix shell: LD_LIBRARY_PATH set for numpy/OpenCV etc."
'';
}

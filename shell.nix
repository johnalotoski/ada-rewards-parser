let
  pkgs = import ./nix { };
  sources = import nix/sources.nix;

  bech32 = (import sources.cardano-node { gitrev = sources.cardano-node.rev; }).bech32;
in with pkgs; mkShell {
  buildInputs = with pkgs; [
    bech32
    python3
    python3Packages.black
    python3Packages.docopt
    python3Packages.flake8
    python3Packages.ipython
    mypy
    niv
  ];
}

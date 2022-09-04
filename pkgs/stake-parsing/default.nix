{
  python3Packages,
}:
with python3Packages;

buildPythonPackage rec {
  pname = "stake-parsing";
  version = "1.0.0";

  propagatedBuildInputs = [
    docopt
  ];

  src = ./.;
}

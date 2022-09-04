{
  python3Packages,
}:
with python3Packages;

buildPythonPackage rec {
  pname = "treasury-parsing";
  version = "1.0.0";

  propagatedBuildInputs = [
    docopt
  ];

  src = ./.;
}

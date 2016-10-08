# State

DEBUG=0

# Colours

RED=31
GREEN=32
YELLOW=33
BLUE=34
LIGHT_GRAY=37

# Helpers

debug() {
  message=$1
  if [ $DEBUG -eq 0 ]; then
    return
  fi

  print_coloured_msg "$message" $LIGHT_GRAY
}

info() {
  message=$1
  print_coloured_msg "$message" $BLUE
}

error() {
  message=$1
  print_coloured_msg "$message" $RED
}

warning() {
  message=$1
  print_coloured_msg "$message" $YELLOW
}

success() {
  message=$1
  print_coloured_msg "$message" $GREEN
}

# Main printing function

print_coloured_msg() {
  message=$1
  colour=$2
  echo -e "\033[${colour}m${message}\033[0m"
}


#
# Scalingo
#
# Show current $SCALINGO_REGION if applicable

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

SPACESHIP_SCALINGO_SHOW="${SPACESHIP_SCALINGO_SHOW=true}"
SPACESHIP_SCALINGO_ASYNC="${SPACESHIP_SCALINGO_ASYNC=true}"
SPACESHIP_SCALINGO_PREFIX="${SPACESHIP_SCALINGO_PREFIX="$SPACESHIP_PROMPT_DEFAULT_PREFIX"}"
SPACESHIP_SCALINGO_SUFFIX="${SPACESHIP_SCALINGO_SUFFIX="$SPACESHIP_PROMPT_DEFAULT_SUFFIX"} "
SPACESHIP_SCALINGO_SYMBOL="${SPACESHIP_SCALINGO_SYMBOL="Scalingo: "}"
SPACESHIP_SCALINGO_COLOR="${SPACESHIP_SCALINGO_COLOR="red"}"
SPACESHIP_SCALINGO_DEV_COLOR="${SPACESHIP_SCALINGO_DEV_COLOR="blue"}"
SPACESHIP_SCALINGO_STAGING_COLOR="${SPACESHIP_SCALINGO_STAGING_COLOR="yellow"}"

# ------------------------------------------------------------------------------
# Section
# ------------------------------------------------------------------------------

# Show scalingo status
# spaceship_ prefix before section's name is required!
# Otherwise this section won't be loaded.
spaceship_scalingo() {
  # If SPACESHIP_SCALINGO_SHOW is false, don't show scalingo section
  [[ $SPACESHIP_SCALINGO_SHOW == false ]] && return

  # Check if $SCALINGO_REGION is defined
  [[ -v SCALINGO_REGION ]] || return

  local scalingo_region="${SCALINGO_REGION}"

  local scalingo_color="$SPACESHIP_SCALINGO_COLOR"
  case $SCALINGO_ENV in
    dev)
      scalingo_color="$SPACESHIP_SCALINGO_DEV_COLOR"
      ;;
    staging)
      scalingo_color="$SPACESHIP_SCALINGO_STAGING_COLOR"
      ;;
  esac

  # Display scalingo section
  # spaceship::section utility composes sections. Flags are optional
  spaceship::section::v4 \
    --color "$scalingo_color" \
    --prefix "$SPACESHIP_SCALINGO_PREFIX" \
    --suffix "$SPACESHIP_SCALINGO_SUFFIX" \
    --symbol "$SPACESHIP_SCALINGO_SYMBOL" \
    "$scalingo_region"
}

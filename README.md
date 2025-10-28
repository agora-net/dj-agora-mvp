# Agora

## Design

Follow the UK Government styleguide and always consider [the design principles](https://www.gov.uk/guidance/government-design-principles).

### Templates

Follow the [UK Gov Page Template](https://design-system.service.gov.uk/styles/page-template/) layout. Simple but flexible.

## Deployment

### Setup

1. Install Caddy
1. Setup a new `agora` user and group with `/home/agora/` directory and all permissions to `agora` user
1. Add Caddy user to `agora` group: `sudo usermod -aG agora caddy`
1. Clone project into project directory `git clone git@github.com:agora-net/dj-agora-mvp.git /home/agora/projects/mvp`
1. Set up the systemctl and Caddy files

## Why this is needed

- [Reddit: a16z-Backed Startup Sells Thousands of ‘Synthetic Influencers’ to Manipulate Social Media as a Service | The company uses "phone farms" of AI-generated accounts and advertises: "Never pay a human again."](https://www.reddit.com/r/Futurology/comments/1ogfaij/a16zbacked_startup_sells_thousands_of_synthetic/)

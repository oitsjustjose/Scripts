#!/bin/bash



# --------------------------------------------------------- #
# RC-file discovery                                         #
# --------------------------------------------------------- #

# Try to use zshrc, but if no zsh use bash
RC_FILE=$(realpath ~/.zshrc)
IS_ZSH=true

if [ ! -f $RC_FILE ] ;
then
    RC_FILE=$(realpath ~/.bashrc)
    IS_ZSH=false
fi

echo "Using ${RC_FILE} as rcfile"

# --------------------------------------------------------- #
# bat -- a syntax-aware, themable cat replacement           #
# --------------------------------------------------------- #


BAT_VERSION="0.18.1"
BAT_THEME="Nord"

echo "Installing Bat Version ${BAT_VERSION}"
wget -q "https://github.com/sharkdp/bat/releases/download/v${BAT_VERSION}/bat-musl_${BAT_VERSION}_amd64.deb" 2>&1>/dev/null
sudo dpkg -i "bat-musl_${BAT_VERSION}_amd64.deb" 2>&1>/dev/null
rm "bat-musl_${BAT_VERSION}_amd64.deb"

# Add the nord theme variable
if /bin/cat "$RC_FILE" | grep -i "export BAT_THEME=" > /dev/null;
then
    echo "Theme is already installed -- NOT overriden"
else
    echo "export BAT_THEME=${BAT_THEME}" >> ~/.zshrc
    echo "Set bat theme to ${BAT_THEME}"
fi


# --------------------------------------------------------- #
# delta -- a replacement for `git diff`                     #
# --------------------------------------------------------- #

DELTA_VERSION="0.8.0"

echo "Installing Delta Version ${DELTA_VERSION}"
wget -q "https://github.com/dandavison/delta/releases/download/${DELTA_VERSION}/git-delta-musl_${DELTA_VERSION}_amd64.deb"
sudo dpkg -i "git-delta-musl_${DELTA_VERSION}_amd64.deb" 2>&1>/dev/null
rm "git-delta-musl_${DELTA_VERSION}_amd64.deb"

# Alias diff to delta
if /bin/cat "$RC_FILE" | grep -e "alias diff=delta" > /dev/null;
then
    echo "Diff is already aliased to delta. Skipping.."
else
    echo "Aliasing diff to delta"
    echo "alias diff=delta" >> $RC_FILE
fi


# --------------------------------------------------------- #
# dust - a more visual, yet slower, du                      #
# --------------------------------------------------------- #


DUST_VERSION="0.5.4"

echo "Installing Dust Version ${DUST_VERSION}"

wget -q "https://github.com/bootandy/dust/releases/download/v${DUST_VERSION}/dust-v${DUST_VERSION}-x86_64-unknown-linux-musl.tar.gz"
tar -xzf "dust-v${DUST_VERSION}-x86_64-unknown-linux-musl.tar.gz"
rm "dust-v${DUST_VERSION}-x86_64-unknown-linux-musl.tar.gz"
sudo mv dust-v0.5.4-x86_64-unknown-linux-musl/dust /usr/local/bin
rm -r "dust-v${DUST_VERSION}-x86_64-unknown-linux-musl"

# --------------------------------------------------------- #
# duf - a more visual df alternative                        #
# --------------------------------------------------------- #

DUF_VERSION="0.6.2"

echo "Installing Duf Version ${DUF_VERSION}"

wget -q "https://github.com/muesli/duf/releases/download/v${DUF_VERSION}/duf_${DUF_VERSION}_linux_amd64.deb"
sudo dpkg -i "duf_${DUF_VERSION}_linux_amd64.deb"
rm "duf_${DUF_VERSION}_linux_amd64.deb"

# Alias df to duf
if /bin/cat "$RC_FILE" | grep -e "alias df=duf" > /dev/null;
then
    echo "Df is already aliased to duf. Skipping.."
else
    echo "Aliasing df to duf"
    echo "alias df=duf" >> $RC_FILE
fi


# --------------------------------------------------------- #
# McFly - a faster alt to ctrl+r rev search                 #
# --------------------------------------------------------- #

MCF_VERSION="0.5.6"

echo "Installing mcfly Version ${MCF_VERSION}"

wget -q "https://github.com/cantino/mcfly/releases/download/v${MCF_VERSION}/mcfly-v${MCF_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
tar -xzf "mcfly-v${MCF_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
rm "mcfly-v${MCF_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
sudo mv mcfly /usr/local/bin

rm mcfly.bash mcfly.fish mcfly.zsh 2>&1 > /dev/null

if /bin/cat "$RC_FILE" | grep -i 'mcfly init' > /dev/null;
then
    echo "Looks like mcfly init script is already in ${RC_FILE}!"
else
    if [ "$IS_ZSH" = true ];
    then
        echo 'eval "$(mcfly init zsh)"' >> "$RC_FILE"
    else
        echo 'eval "$(mcfly init bash)"' >> "$RC_FILE"
    fi
    echo "Added McFly init to ${RC_FILE}"
fi


# --------------------------------------------------------- #
# GTOP - a nicer TOP GUI, requires Node...                  #
# --------------------------------------------------------- #

if command -v npm &> /dev/null && ! which npm | grep /mnt/c/ &> /dev/null ;
then
    echo "Installing GTOP via NPM"
    npm i -g gtop
else
    if command -v docker &> /dev/null ;
    then
        echo "Installing GTOP via Docker"
        if /bin/cat "$RC_FILE" | grep -i 'alias gtop=' > /dev/null;
        then
            echo "Looks like gtop is already aliased!"
        else
            echo $'alias gtop=\'docker run --rm -it --name gtop --net=host --pid=host aksakalli/gtop\'' >> "$RC_FILE"
            echo $'eval "$(alias gtop=\'docker run --rm -it --name gtop --net=host --pid=host aksakalli/gtop\')"' >> "$RC_FILE"
        fi
    else
        echo "Neither NPM nor Docker could not be found, skipping GTOP installation"
    fi
fi

echo "Done installing tools! Restarting shell"
exec "$SHELL"

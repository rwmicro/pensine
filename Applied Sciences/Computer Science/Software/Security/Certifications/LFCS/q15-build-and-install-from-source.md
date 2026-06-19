# Question 15 — Build and install from source

## Notes d'apprentissage

Installer depuis les sources, c'est compiler le code soi-même au lieu d'utiliser un paquet précompilé (`apt`/`dnf`). Utile quand le logiciel n'est pas packagé, qu'on veut une version précise ou des options de compilation particulières.

**Modèle mental : le trio `configure / make / make install`.**

```
sources (.tar.bz2)
   │  tar xjf
   ▼
./configure   ── détecte l'environnement, génère le Makefile selon vos options
   │
make          ── compile le code source en binaires
   │
make install  ── copie les binaires aux emplacements système (souvent en root)
```

C'est la chaîne « autotools » historique des projets C/C++. Chaque étape a un rôle distinct ; les sauter ou les inverser ne marche pas.

**`./configure` : c'est là que les options se posent.** Il accepte des drapeaux qui pilotent la compilation :
```bash
./configure --help                   # lister TOUTES les options du projet
./configure --prefix=/usr            # où sera installé (binaires dans /usr/bin)
./configure --disable-ipv6           # désactiver une fonctionnalité
./configure --enable-X --with-Y      # activer des options / lier des bibliothèques
```
`--prefix` est la clé pour contrôler l'emplacement final : `--prefix=/usr` met le binaire dans `/usr/bin`. Les `--disable-*`/`--enable-*` activent/désactivent des fonctionnalités à la compilation.

**Pré-requis : les outils de build.** Il faut un compilateur et les en-têtes des dépendances, sinon `configure` ou `make` échoue :
```bash
sudo apt install build-essential        # gcc, make, etc. (Debian)
sudo dnf groupinstall "Development Tools" # équivalent RHEL
```

**Vérifier le résultat :**
```bash
make install
which links            # /usr/bin/links
links -version
```

**Pièges** :
- Lire le `README`/`INSTALL` de l'archive : chaque projet a ses spécificités.
- `make install` écrit dans des emplacements système → souvent `sudo` nécessaire.
- Une erreur en plein `make` vient presque toujours d'une **dépendance manquante** (un `*-dev`/`*-devel`) signalée plus tôt par `configure`.
- Un logiciel installé depuis les sources **échappe au gestionnaire de paquets** : pas de mise à jour ni de désinstallation automatiques (`make uninstall` si fourni). Voir [[q26-package-management]].

## Énoncé

Solve this question on: `app-srv1`

Install the text based terminal browser `links2` from source on server `app-srv1`. The source is provided at `/tools/links-2.14.tar.bz2` on that server.

Configure the installation process so that:
1. The target location of the installed binary will be `/usr/bin/links`
2. Support for ipv6 will be disabled

## Solution

Let's first check out the provided archive and extract it's content:
```bash
ssh app-srv1
root@app-srv1:~$ cd /tools
root@app-srv1:/tools$ ls
links-2.14.tar.bz2
```

We'll go ahead and extract the archive:
```bash
root@app-srv1:/tools$ tar xjf links-2.14.tar.bz2
root@app-srv1:/tools$ cd links-2.14
root@app-srv1:/tools/links-2.14$ ls -lh
total 6.9M
-rw-r--r-- 1 ubuntu ubuntu 9.2K Aug 12  2015 AUTHORS
-rw-r--r-- 1 ubuntu ubuntu 1.2K Jan  2  2005 BRAILLE_HOWTO
-rw-r--r-- 1 ubuntu ubuntu  19K Sep 21  2013 COPYING
-rw-r--r-- 1 ubuntu ubuntu 114K Nov 26  2016 ChangeLog
-rw-r--r-- 1 ubuntu ubuntu 4.6K Nov 26  2016 INSTALL
-rw-r--r-- 1 ubuntu ubuntu 1.9K Apr  9  2012 KEYS
-rw-r--r-- 1 ubuntu ubuntu  650 Jan 10  2005 Links_logo.png
-rw-r--r-- 1 ubuntu ubuntu 2.6K Jun 16  2016 Makefile.am
-rw-r--r-- 1 ubuntu ubuntu  22K Nov  3  2016 Makefile.in
-rw-r--r-- 1 ubuntu ubuntu  214 Feb 11  2012 NEWS
...
```

The usual process of installing from source is:
1. `./configure (args...)`
2. `make`
3. `make install`
Here the question requires specific configuration parameters. We can list all possible options:
```bash
root@app-srv1:/tools/links-2.14$ ./configure -help
Usage: configure [options] [host]
Options: [defaults in brackets after descriptions]
Configuration:
  --cache-file=FILE       cache test results in FILE
  --help                  print this message
  --no-create             do not create output files
  --quiet, --silent       do not print checking... messages
  --version               print the version of autoconf that created configure
```

Directory and file names:

  --prefix=PREFIX         install architecture-independent files in PREFIX    # !! USEFUL

                          [/usr/local]

  --exec-prefix=EPREFIX   install architecture-dependent files in EPREFIX

                          [same as prefix]

  --bindir=DIR            user executables in DIR [EPREFIX/bin]

  --sbindir=DIR           system admin executables in DIR [EPREFIX/sbin]

  --libexecdir=DIR        program executables in DIR [EPREFIX/libexec]

  --datadir=DIR           read-only architecture-independent data in DIR

                          [PREFIX/share]

  --sysconfdir=DIR        read-only single-machine data in DIR [PREFIX/etc]

  --sharedstatedir=DIR    modifiable architecture-independent data in DIR

                          [PREFIX/com]

...

  --enable-graphics       use graphics

  --disable-utf8          disable UTF-8 terminal (saves memory)

  --without-getaddrinfo   compile without getaddrinfo function

  --without-ipv6          compile without ipv6                                # !! USEFUL

  --without-libevent      compile without libevent

  --without-gpm           compile without gpm mouse

  --with-ssl(=directory)  enable SSL support

  --with-ssl=nss          enable SSL support through NSS OpenSSL emulation

  --disable-ssl-pkgconfig don't use pkgconfig when searching for openssl

...

It's also possible to open the `./configure` file in a text editor to investigate possible options if the help output won't suffice.

We now use the following configuration:
```bash
root@app-srv1:/tools/links-2.14$ ./configure --prefix /usr --without-ipv6
creating cache ./config.cache
checking for a BSD compatible install... /usr/bin/install -c
checking whether build environment is sane... yes
checking whether make sets ${MAKE}... yes
checking for working aclocal-1.4... missing
checking for working autoconf... missing
...
creating ./config.status
creating Makefile
creating config.h
---------------------------------------------------------
Configuration results:
Event handler:          NO
IPv6:                   NO
Supported compression:  NO
SSL support:            NO
UTF-8 terminal:         YES
GPM support:            NO
Graphics enabled:       NO
---------------------------------------------------------
```

After the configuration we continue with `make`:
```bash
root@app-srv1:/tools/links-2.14$ make
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c af_unix.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c auth.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c beos.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c bfu.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c block.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c bookmark.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c cache.c
...
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c vms.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c x.c
gcc -DHAVE_CONFIG_H -I. -I. -I.     -g -O2 -c xbm.c
gcc  -g -O2  -o links  af_unix.o auth.o beos.o bfu.o block.o bookmark.o cache.o charsets.o compress.o connect.o cookies.o data.o default.o dip.o directfb.o dither.o dns.o dos.o drivers.o error.o file.o finger.o fn_impl.o font_inc.o framebuf.o ftp.o gif.o grx.o hpux.o html.o html_gr.o html_r.o html_tbl.o http.o https.o img.o imgcache.o jpeg.o jsint.o kbd.o language.o listedit.o lru.o mailto.o main.o memory.o menu.o objreq.o os_dep.o pmshell.o png.o sched.o select.o session.o smb.o string.o suffix.o svg.o svgalib.o terminal.o tiff.o types.o url.o view.o view_gr.o vms.o x.o xbm.o  -lpthread
/usr/bin/ld: session.o: in function `get_temp_name':
/tools/links-2.14/session.c:1056: warning: the use of `tempnam' is dangerous, better use `mkstemp'
```

Followed by the `make install`:
```bash
root@app-srv1:/tools/links-2.14$ make install
make[1]: Entering directory '/tools/links-2.14'
/bin/sh ./mkinstalldirs /usr/bin
  /usr/bin/install -c  links /usr/bin/links
make  install-man1
make[2]: Entering directory '/tools/links-2.14'
/bin/sh ./mkinstalldirs /usr/man/man1
 /usr/bin/install -c -m 644 ./links.1 /usr/man/man1/links.1
make[2]: Leaving directory '/tools/links-2.14'
make[1]: Leaving directory '/tools/links-2.14'
```

This should result in:
```bash
root@app-srv1:~$ whereis links
links: /usr/bin/links /usr/man/man1/links.1
root@app-srv1:~$ /usr/bin/links -version
Links 2.14
```

We can verify that ipv6 is disabled:
```bash
root@app-srv1:~$ /usr/bin/links -lookup ip6-localhost
error: host not found         # output if ipv6 is disabled
root@app-srv1:~$ /usr/bin/links -lookup ip6-localhost
::1                           # output if ipv6 is enabled
```

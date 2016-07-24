## Process this file with automake to produce Makefile.in
<<<<<<< HEAD
=======

>>>>>>> e238d312a17739cf2311261c8becf796418bdb2d
## Created by Anjuta



<<<<<<< HEAD
## The main script
bin_SCRIPTS = bfxconsole.py

## Directory where .class files will be installed
bfxconsoledir = $(pythondir)/bfxconsole


bfxconsole_PYTHON = \
	bfxconsole.py



# Remove ui directory on uninstall
uninstall-local:

	-rm -r $(pkgdatadir)
=======
AM_CPPFLAGS = \
	-DPACKAGE_LOCALE_DIR=\""$(localedir)"\" \
	-DPACKAGE_SRC_DIR=\""$(srcdir)"\" \
	-DPACKAGE_DATA_DIR=\""$(pkgdatadir)"\" \
	$(BFXCONSOLE_CFLAGS)

AM_CFLAGS =\
	 -Wall\
	 -g

bin_PROGRAMS = bfxconsole

bfxconsole_SOURCES = \
	bfxconsole.vala config.vapi

bfxconsole_VALAFLAGS =  --pkg json-glib-1.0 --pkg libsoup-2.4 --pkg glib-2.0 --pkg gtk+-3.0 --pkg gio-2.0  \
	--pkg gtk+-3.0


bfxconsole_LDFLAGS = \
	-Wl,--export-dynamic

bfxconsole_LDADD = $(BFXCONSOLE_LIBS)




>>>>>>> e238d312a17739cf2311261c8becf796418bdb2d

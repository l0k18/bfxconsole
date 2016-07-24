## Process this file with automake to produce Makefile.in

## Created by Anjuta



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





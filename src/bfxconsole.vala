/* bfxconsole.vala
 *
 * License Notice
 *
 * License means permission from a privileged party to do something that would
 * otherwise be a crime, upon their property. This document sits upon your
 * property and you granted licence to its presence there by placing it there.
 *
 * Copyright is nothing more than a monopoly grant privilege, and I don't
 * acknowledge any monopoly other than of a natural person upon their property.
 *
 * Thus since this is now your property, if it messes your shit up, that's not
 * my problem, I am just a simple program writer, and I didn't ask you to
 * place this file upon your computer, or any derivative of this file such as
 * a compiled version that you can run on your computer.
 *
 * Since it is currently residing on your property, you are free to do whatever
 * you want with this file, with no restrictions.
 *
 * The fact that I have to explain these things is sad.
 *
 */

using GLib;
using Soup;
using Gtk;

public class bfxconsole : Gtk.Application {
    private GLib.Settings settings;
    private Gtk.ApplicationWindow window;

	public bfxconsole () {
		Object(application_id: "org.ascension.bfxconsole",
				flags: ApplicationFlags.FLAGS_NONE);
	}

    public void bfx_settings () {
        Gtk.Button setkeys;
        Gtk.Grid grid;
        Gtk.Entry apikey;
        Gtk.Entry apisecret;

        grid = new Gtk.Grid ();
        grid.attach (new Gtk.Label (" Please enter your Bitfinex API key details: "), 1, 1, 3, 1);
        grid.attach (new Gtk.Label (" API Key: "), 1, 2, 1, 1);
        apikey = new Gtk.Entry ();
        grid.attach (apikey, 2, 2, 1, 1);
        grid.attach (new Gtk.Label (" API Secret: "), 1, 3, 1, 1);
        apisecret = new Gtk.Entry ();
        grid.attach (apisecret, 2, 3, 1, 1);
        setkeys = new Gtk.Button.with_label ("Ok");
        setkeys.set_sensitive (false);
        grid.attach (setkeys, 1, 4, 2, 1);
        window.child = grid;
        grid.show_all ();

        apikey.changed.connect ( () => {
            if (apikey.text_length == 43 &&
                apisecret.text_length == 43)
                setkeys.set_sensitive (true);
                else setkeys.set_sensitive (false);
        });

        apisecret.changed.connect ( () => {
            if (apisecret.text_length == 43 &&
                apikey.text_length == 43)
                setkeys.set_sensitive (true);
                else setkeys.set_sensitive (false);
        });

        setkeys.clicked.connect ( () => {
            settings.set_string ("apikey", apikey.get_text());
            settings.set_string ("apisecret", apisecret.get_text());
            var uri = "https://api.bitfinex.com/v1";
            var session = new Soup.Session ();
            var message = new Soup.Message ("GET", uri);
    });

    }

    private bool apikeys_are_set () {
        if (settings.get_string ("apikey") == "" ||
            settings.get_string ("apisecret") == "") return true;
            else return false;
    }

	protected override void activate () {
		window = new Gtk.ApplicationWindow (this);
		window.set_default_size (100, 100);
        window.set_position(Gtk.WindowPosition.CENTER);
		window.title = "bfxconsole";
		window.show_all ();

        settings = new GLib.Settings ("org.ascension.bfxconsole");

        if (apikeys_are_set ()) bfx_settings ();
	}

	public static int main (string[] args) {
		bfxconsole app = new bfxconsole ();
		return app.run (args);
	}
}

using Soup;
using GLib;
using Gtk;

void main () {
    var uri = "http://services.gisgraphy.com/fulltext/fulltextsearch?q=%s&format=JSON&indent=true&lang=en&from=1&to=10".printf ("asakusa");

    var session = new Soup.Session ();
    var message = new Soup.Message ("GET", uri);
    session.send_message (message);

    try {
        var parser = new Json.Parser ();
        parser.load_from_data ((string) message.response_body.flatten ().data, -1);

        var root_object = parser.get_root ().get_object ();
        var response = root_object.get_object_member ("response");
        var results = response.get_array_member ("docs");
        int64 count = results.get_length ();
        int64 total = response.get_int_member ("numFound");
        stdout.printf ("got %lld out of %lld results:\n\n", count, total);

        foreach (var geonode in results.get_elements ()) {
            var geoname = geonode.get_object ();
            stdout.printf ("%s\n%s\n%f\n%f\n\n",
                          geoname.get_string_member ("name"),
                          geoname.get_string_member ("country_name"),
                          geoname.get_double_member ("lng"),
                          geoname.get_double_member ("lat"));
        }
    } catch (Error e) {
        stderr.printf ("I guess something is not working...\n");
    }
}


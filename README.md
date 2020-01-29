## Q: How to pronounce enpda?

A: In formal contexts /eᶦn peᶦdeᶦaʊ/ but in casual conversation
/eːn peːdeːaʊ/ is fine too.

But really, I'm a descriptivist, pronounce it however you want,
that's what you were going to do anyways.

## Q: What is it?

**This is very early prototype software**

A PDA, a "Personal Digital Assistant". My goal is to have a
dedicated device booting straight into this, a device that does
not have an ideal size keyboard nor keyboard layout. (Yes, I have
a specific device in mind, glad you asked.)

After having considered (and tried to build, but failed)
something webkit based, I reconsidered and delighted over the
idea of having a framebuffer console based TUI environment for
this use case. I use the python library [urwid](urwid) to create
the interface.

The current "apps" are:

 * a notes taking application
 * a fosdem schedule viewer
 * a syslog viewer (... cat /var/log/syslog)

I hope to find use for it during FOSDEM 2020, hence the focus.

### Follwup Q: FOSDEM schedule viewer only? What about conference X?

For some values of X, it turns out they have XML exports of their
scheudle that are compatible with that of FOSDEM. I made
assumtions about this being used for FOSDEM, but "I heard" that
it works well for at least CCC as well.

This could be generalized to a browser of conferences, where we
can load arbitrary number of such XML files and organize them in
a tree structure, like `<conference>/<track>/<event>` (currently
only `<track>/<event>`).

At some point, I'll probably visit conferences without this XML
export, and I'll have to add something like ical support :-(.

## Q: Can I try it?

I created a wrapper to make it easier to run it on your regular
machine, but it does require two steps of preparation:

Standing in the top level of the repository, create the directory
"data" (must be "data", or you'll have to modify the
`bin/enpda-test` script):

```
mkdir data
```

Download a conference schedule XML, compatible with that of
FOSDEM (name it fosdem.xml regardless of what conference it is):

```
curl -o data/fosdem.xml -L https://fosdem.org/2020/schedule/xml
```

And after this, you can run the script:

```
bin/enpda-test
```

## Q: What device are you targeting?

This cute little thing: [GPD Pocket 1][gpd-pocket-1].

But if somebody would like to buy me a [Gemini PDA][gemini], I
would love to support that too ;-).

I'm doing this with OpenEmbedded, and I plan to publish the
layers I created for this project, including a generic bsp layer
for gpd with necessary kernel configs. (I should probably fix
those `LICENSE = "CLOSED"` recipes first though... :p)

[gpd-pocket-1]: https://www.gpd.hk/gpdpocket/
[gemini]: https://store.planetcom.co.uk/collections/devices/products/gemini-pda-1?variant=6331545616411
[urwid]: http://urwid.org/

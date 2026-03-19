export function Footer() {
  return (
    <footer className="bg-gray-100 border-t border-gray-200 mt-20">
      <div className="max-w-5xl mx-auto px-6 py-10 md:py-12 grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">

        {/* COMPANY */}
        <div>
          <h3 className="text-base font-semibold mb-3">Uniforma</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            Arbetskläder och profilplagg för professionella miljöer.
          </p>
          <div className="mt-4 space-y-1.5 text-sm text-gray-600">
            <p>E-post: info@uniforma.se</p>
            <p>Telefon: 070-000 00 00</p>
            <p>Adress: Sverige</p>
          </div>
        </div>

        {/* NAVIGATION */}
        <div>
          <h3 className="text-base font-semibold mb-3">Navigation</h3>
          <ul className="space-y-1.5 text-sm text-gray-600">
            <li><a href="/" className="hover:text-black transition">Startsida</a></li>
            <li><a href="/shop" className="hover:text-black transition">Produkter</a></li>
            <li><a href="/om-oss" className="hover:text-black transition">Om oss</a></li>
            <li><a href="/kontakt" className="hover:text-black transition">Kontakt</a></li>
            <li><a href="/storleksguide" className="hover:text-black transition">Storleksguide</a></li>
          </ul>
        </div>

      </div>

      <div className="border-t border-gray-200 text-center text-xs text-gray-500 py-3">
        © {new Date().getFullYear()} Uniforma. Alla rättigheter förbehållna.
      </div>
    </footer>
  );
}

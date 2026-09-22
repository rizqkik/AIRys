import airys_ui

app = airys_ui.init_ui()
app.set_status("aktif")
app.tambah_pesan("system", "Sistem dimulai")
app.tambah_pesan("airys", "Halo Bos Rizqi, AIRys online.")
app.run()

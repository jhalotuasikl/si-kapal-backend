-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 08 Apr 2026 pada 03.23
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `si_kapal`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `detail_jawaban_kuisoner`
--

CREATE TABLE `detail_jawaban_kuisoner` (
  `id_detail_jawaban` int(11) NOT NULL,
  `id_jawaban` int(11) NOT NULL,
  `id_pertanyaan` int(11) NOT NULL,
  `pilihan` enum('A','B','C','D') NOT NULL,
  `skor` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `detail_jawaban_kuisoner`
--

INSERT INTO `detail_jawaban_kuisoner` (`id_detail_jawaban`, `id_jawaban`, `id_pertanyaan`, `pilihan`, `skor`) VALUES
(11, 2, 1, 'A', 100),
(12, 2, 2, 'A', 100),
(13, 2, 3, 'A', 100),
(14, 2, 4, 'A', 100),
(15, 2, 5, 'A', 100),
(16, 2, 6, 'A', 100),
(17, 2, 7, 'A', 100),
(18, 2, 8, 'A', 100),
(19, 2, 9, 'A', 100),
(20, 2, 10, 'A', 100);

-- --------------------------------------------------------

--
-- Struktur dari tabel `guru`
--

CREATE TABLE `guru` (
  `id_guru` int(11) NOT NULL,
  `nip` varchar(30) NOT NULL,
  `nama_guru` varchar(100) NOT NULL,
  `mata_pelajaran` varchar(100) NOT NULL,
  `id_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `guru`
--

INSERT INTO `guru` (`id_guru`, `nip`, `nama_guru`, `mata_pelajaran`, `id_user`) VALUES
(2, '20122', 'jhalopax', '', 9),
(5, '12345', 'avatar', '', 18);

-- --------------------------------------------------------

--
-- Struktur dari tabel `guru_mapel`
--

CREATE TABLE `guru_mapel` (
  `id_guru` int(11) NOT NULL,
  `id_mapel` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `jadwal`
--

CREATE TABLE `jadwal` (
  `id_jadwal` int(11) NOT NULL,
  `id_kelas` int(11) NOT NULL,
  `id_mapel` int(11) NOT NULL,
  `hari` enum('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu') NOT NULL,
  `jam_mulai` time NOT NULL,
  `jam_selesai` time NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `jadwal`
--

INSERT INTO `jadwal` (`id_jadwal`, `id_kelas`, `id_mapel`, `hari`, `jam_mulai`, `jam_selesai`, `created_at`) VALUES
(6, 6, 7, 'Rabu', '12:30:00', '15:00:00', '2026-03-11 00:15:03'),
(9, 6, 10, 'Kamis', '09:10:00', '11:10:00', '2026-03-12 02:00:28');

-- --------------------------------------------------------

--
-- Struktur dari tabel `jadwal_guru`
--

CREATE TABLE `jadwal_guru` (
  `id_jadwal_guru` int(11) NOT NULL,
  `id_jadwal` int(11) NOT NULL,
  `id_guru` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `jadwal_guru`
--

INSERT INTO `jadwal_guru` (`id_jadwal_guru`, `id_jadwal`, `id_guru`) VALUES
(6, 6, 2),
(10, 9, 2);

-- --------------------------------------------------------

--
-- Struktur dari tabel `jadwal_murid`
--

CREATE TABLE `jadwal_murid` (
  `id_jadwal` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `jadwal_murid`
--

INSERT INTO `jadwal_murid` (`id_jadwal`, `id_murid`) VALUES
(6, 10);

-- --------------------------------------------------------

--
-- Struktur dari tabel `jawaban_kuisoner`
--

CREATE TABLE `jawaban_kuisoner` (
  `id_jawaban` int(11) NOT NULL,
  `id_kuisoner` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `tanggal_kirim` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `jawaban_kuisoner`
--

INSERT INTO `jawaban_kuisoner` (`id_jawaban`, `id_kuisoner`, `id_murid`, `tanggal_kirim`) VALUES
(2, 2, 10, '2026-03-10 17:25:33');

-- --------------------------------------------------------

--
-- Struktur dari tabel `kehadiran_guru`
--

CREATE TABLE `kehadiran_guru` (
  `id_kehadiran` int(11) NOT NULL,
  `id_guru` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `status` enum('Hadir','Izin','Sakit','Alpa') NOT NULL,
  `keterangan` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `kehadiran_murid`
--

CREATE TABLE `kehadiran_murid` (
  `id_kehadiran` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `pertemuan` int(11) NOT NULL,
  `status` varchar(20) NOT NULL,
  `id_jadwal` int(11) NOT NULL,
  `tanggal` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kehadiran_murid`
--

INSERT INTO `kehadiran_murid` (`id_kehadiran`, `id_murid`, `pertemuan`, `status`, `id_jadwal`, `tanggal`) VALUES
(16, 10, 1, 'Hadir', 6, '2026-03-11'),
(17, 10, 2, 'Hadir', 6, '2026-03-12'),
(18, 10, 3, 'Hadir', 6, '2026-03-12'),
(19, 10, 4, 'Izin', 6, '2026-03-12'),
(20, 10, 5, 'Alpa', 6, '2026-03-12'),
(21, 10, 1, 'Hadir', 9, '2026-03-12'),
(22, 10, 2, 'Hadir', 9, '2026-03-12'),
(23, 10, 3, 'Hadir', 9, '2026-03-12'),
(24, 10, 4, 'Sakit', 9, '2026-03-12'),
(25, 10, 5, 'Hadir', 9, '2026-04-08'),
(26, 10, 6, 'Hadir', 9, '2026-04-08');

-- --------------------------------------------------------

--
-- Struktur dari tabel `kelas`
--

CREATE TABLE `kelas` (
  `id_kelas` int(11) NOT NULL,
  `nama_kelas` varchar(50) NOT NULL,
  `tahun_ajaran` varchar(20) NOT NULL,
  `id_tingkat` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kelas`
--

INSERT INTO `kelas` (`id_kelas`, `nama_kelas`, `tahun_ajaran`, `id_tingkat`) VALUES
(6, 'KELAS A', '2026', 3);

-- --------------------------------------------------------

--
-- Struktur dari tabel `kelas_guru`
--

CREATE TABLE `kelas_guru` (
  `id_kelas` int(11) NOT NULL,
  `id_guru` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `kelas_mapel`
--

CREATE TABLE `kelas_mapel` (
  `id_kelas` int(11) NOT NULL,
  `id_mapel` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kelas_mapel`
--

INSERT INTO `kelas_mapel` (`id_kelas`, `id_mapel`) VALUES
(6, 7),
(6, 10);

-- --------------------------------------------------------

--
-- Struktur dari tabel `kuisoner`
--

CREATE TABLE `kuisoner` (
  `id_kuisoner` int(11) NOT NULL,
  `id_jadwal` int(11) NOT NULL,
  `semester` varchar(10) NOT NULL,
  `tahun_ajaran` varchar(20) NOT NULL,
  `status` enum('belum_dibuka','dibuka','ditutup','selesai') DEFAULT 'belum_dibuka',
  `tanggal_dibuka` datetime DEFAULT NULL,
  `tanggal_ditutup` datetime DEFAULT NULL,
  `dibuat_pada` timestamp NOT NULL DEFAULT current_timestamp(),
  `diupdate_pada` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `kuisoner`
--

INSERT INTO `kuisoner` (`id_kuisoner`, `id_jadwal`, `semester`, `tahun_ajaran`, `status`, `tanggal_dibuka`, `tanggal_ditutup`, `dibuat_pada`, `diupdate_pada`) VALUES
(2, 6, '1', '2026/2027', 'selesai', '2026-03-11 00:23:50', '2026-03-12 02:23:31', '2026-03-10 17:23:50', '2026-03-11 19:23:31');

-- --------------------------------------------------------

--
-- Struktur dari tabel `laporan_mengajar`
--

CREATE TABLE `laporan_mengajar` (
  `id_laporan` int(11) NOT NULL,
  `id_monitor` int(11) NOT NULL,
  `materi` text DEFAULT NULL,
  `catatan` text DEFAULT NULL,
  `jumlah_hadir` int(11) DEFAULT 0,
  `waktu_input` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `laporan_monitoring`
--

CREATE TABLE `laporan_monitoring` (
  `id_monitor` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `jam_masuk` time DEFAULT NULL,
  `jam_keluar` time DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `id_jadwal` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `laporan_monitoring`
--

INSERT INTO `laporan_monitoring` (`id_monitor`, `tanggal`, `jam_masuk`, `jam_keluar`, `status`, `id_jadwal`) VALUES
(7, '2026-03-12', '09:02:06', NULL, 'Hadir', 9);

-- --------------------------------------------------------

--
-- Struktur dari tabel `log_aktivitas`
--

CREATE TABLE `log_aktivitas` (
  `id_log` int(11) NOT NULL,
  `id_user` int(11) NOT NULL,
  `aktivitas` varchar(255) NOT NULL,
  `waktu` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `mata_pelajaran`
--

CREATE TABLE `mata_pelajaran` (
  `id_mapel` int(11) NOT NULL,
  `nama_mapel` varchar(100) NOT NULL,
  `id_tingkat` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `mata_pelajaran`
--

INSERT INTO `mata_pelajaran` (`id_mapel`, `nama_mapel`, `id_tingkat`) VALUES
(7, 'Tugas Akhir', 3),
(10, 'NGODING', 3);

-- --------------------------------------------------------

--
-- Struktur dari tabel `murid`
--

CREATE TABLE `murid` (
  `id_murid` int(11) NOT NULL,
  `nis` varchar(30) NOT NULL,
  `nama_murid` varchar(100) NOT NULL,
  `id_kelas` int(11) NOT NULL,
  `id_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `murid`
--

INSERT INTO `murid` (`id_murid`, `nis`, `nama_murid`, `id_kelas`, `id_user`) VALUES
(10, '111', 'Aurelia Hermouns', 6, 17);

-- --------------------------------------------------------

--
-- Struktur dari tabel `murid_mapel`
--

CREATE TABLE `murid_mapel` (
  `id_murid_mapel` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `id_mapel` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `murid_mapel`
--

INSERT INTO `murid_mapel` (`id_murid_mapel`, `id_murid`, `id_mapel`) VALUES
(8, 10, 7);

-- --------------------------------------------------------

--
-- Struktur dari tabel `murid_tingkat`
--

CREATE TABLE `murid_tingkat` (
  `id` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `id_tingkat` int(11) NOT NULL,
  `id_kelas` int(11) NOT NULL,
  `tahun_ajaran` varchar(20) NOT NULL,
  `status` enum('aktif','lulus','pindah') NOT NULL DEFAULT 'aktif',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `murid_tingkat`
--

INSERT INTO `murid_tingkat` (`id`, `id_murid`, `id_tingkat`, `id_kelas`, `tahun_ajaran`, `status`, `created_at`) VALUES
(8, 10, 3, 6, '2025/2026', 'aktif', '2026-03-11 00:16:07');

-- --------------------------------------------------------

--
-- Struktur dari tabel `nilai`
--

CREATE TABLE `nilai` (
  `id_nilai` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `semester` enum('Ganjil','Genap') NOT NULL,
  `tahun_ajaran` varchar(20) NOT NULL,
  `nilai_angka` decimal(5,2) NOT NULL,
  `nilai_huruf` char(2) DEFAULT NULL,
  `id_jadwal` int(11) NOT NULL,
  `status_kirim` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `nilai`
--

INSERT INTO `nilai` (`id_nilai`, `id_murid`, `semester`, `tahun_ajaran`, `nilai_angka`, `nilai_huruf`, `id_jadwal`, `status_kirim`) VALUES
(8, 10, 'Ganjil', '2026/2027', 100.00, 'A', 6, 1);

-- --------------------------------------------------------

--
-- Struktur dari tabel `orang_tua`
--

CREATE TABLE `orang_tua` (
  `id_ortu` int(11) NOT NULL,
  `nama_ortu` varchar(100) NOT NULL,
  `no_hp` varchar(20) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `id_user` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `pengaduan`
--

CREATE TABLE `pengaduan` (
  `id_pengaduan` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `mode_pelaporan` enum('terbuka','rahasia','anonim') NOT NULL,
  `kategori_pengaduan` enum('akademik','absensi','nilai','bullying','fasilitas','lainnya') NOT NULL,
  `isi_pengaduan` text NOT NULL,
  `status` enum('menunggu','diproses','selesai','ditolak') NOT NULL DEFAULT 'menunggu',
  `catatan_admin` text DEFAULT NULL,
  `tanggal_pengaduan` datetime NOT NULL DEFAULT current_timestamp(),
  `tanggal_ditindaklanjuti` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pengaduan`
--

INSERT INTO `pengaduan` (`id_pengaduan`, `id_murid`, `mode_pelaporan`, `kategori_pengaduan`, `isi_pengaduan`, `status`, `catatan_admin`, `tanggal_pengaduan`, `tanggal_ditindaklanjuti`) VALUES
(3, 10, 'terbuka', 'bullying', 'Hentikan bully disekolah ini', 'selesai', 'pihak sekolah akan memprosesnya secepat nya', '2026-03-12 00:01:27', '2026-03-12 00:49:26'),
(4, 10, 'rahasia', 'lainnya', 'pelecehan, terjdi di sni', 'selesai', 'sudah kota atasi', '2026-03-12 02:19:58', '2026-03-12 02:21:04');

-- --------------------------------------------------------

--
-- Struktur dari tabel `penilaian_guru`
--

CREATE TABLE `penilaian_guru` (
  `id_penilaian` int(11) NOT NULL,
  `id_guru` int(11) NOT NULL,
  `id_murid` int(11) NOT NULL,
  `semester` enum('Ganjil','Genap') NOT NULL,
  `skor` int(11) NOT NULL,
  `komentar` text DEFAULT NULL,
  `tanggal` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur dari tabel `pertanyaan_kuisoner`
--

CREATE TABLE `pertanyaan_kuisoner` (
  `id_pertanyaan` int(11) NOT NULL,
  `pertanyaan` text NOT NULL,
  `aktif` tinyint(1) DEFAULT 1,
  `dibuat_pada` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `pertanyaan_kuisoner`
--

INSERT INTO `pertanyaan_kuisoner` (`id_pertanyaan`, `pertanyaan`, `aktif`, `dibuat_pada`) VALUES
(1, 'Apakah kelas dimulai dengan doa?', 1, '2026-03-10 21:38:35'),
(2, 'Apakah pembelajaran dimulai dengan tertib dan teratur?', 1, '2026-03-10 21:38:35'),
(3, 'Apakah materi pelajaran disampaikan dengan jelas?', 1, '2026-03-10 21:38:35'),
(4, 'Apakah suasana kelas mendukung proses belajar dengan baik?', 1, '2026-03-10 21:38:35'),
(5, 'Apakah murid diberi kesempatan untuk bertanya saat pembelajaran berlangsung?', 1, '2026-03-10 21:38:35'),
(6, 'Apakah penjelasan materi mudah dipahami oleh murid?', 1, '2026-03-10 21:38:35'),
(7, 'Apakah contoh yang diberikan saat pembelajaran membantu pemahaman materi?', 1, '2026-03-10 21:38:35'),
(8, 'Apakah tugas yang diberikan sesuai dengan materi yang dipelajari?', 1, '2026-03-10 21:38:35'),
(9, 'Apakah kegiatan belajar berlangsung dengan aktif dan menyenangkan?', 1, '2026-03-10 21:38:35'),
(10, 'Apakah pembelajaran diakhiri dengan kesimpulan atau penutup yang jelas?', 1, '2026-03-10 21:38:35');

-- --------------------------------------------------------

--
-- Struktur dari tabel `roles`
--

CREATE TABLE `roles` (
  `id_role` int(11) NOT NULL,
  `nama_role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `roles`
--

INSERT INTO `roles` (`id_role`, `nama_role`) VALUES
(1, 'admin'),
(2, 'guru'),
(3, 'murid');

-- --------------------------------------------------------

--
-- Struktur dari tabel `tingkat`
--

CREATE TABLE `tingkat` (
  `id_tingkat` int(11) NOT NULL,
  `pangkat` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `tingkat`
--

INSERT INTO `tingkat` (`id_tingkat`, `pangkat`) VALUES
(1, 'I'),
(2, 'II'),
(3, 'III');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id_user` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `id_role` int(11) NOT NULL,
  `status` enum('aktif','nonaktif') NOT NULL DEFAULT 'aktif',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `foto_profil` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id_user`, `username`, `password`, `id_role`, `status`, `created_at`, `foto_profil`) VALUES
(1, 'admin', 'scrypt:32768:8:1$8sW12WORazWdzPKD$1ef0b082302ffddb0b636159342b33d382c5c696068c88a720a4ed4c38f19598f238aefc8449889fa0ef494da94123babdcbb50a6d0a3793581ace38d18d3079', 1, 'aktif', '2026-03-04 05:47:11', NULL),
(9, 'jhalopax467', 'scrypt:32768:8:1$Wi6YZSVLarZKLl1w$74cd3cef49a7751773ac9ecb0a1287d88c2c994a38e697bb35f249ca3bf7e1cd00ca89b0a09447c555de0b22e6f63d4a71904c0b7e8921dd19890e05045f7e26', 2, 'aktif', '2026-03-06 20:36:38', '/static/profile_photos/633e1a93951f44ccbacbaee6004737a5.jpg'),
(17, '111', 'scrypt:32768:8:1$YheNc4wvi5E5D1J0$e66c926256fa2c2b09c8a922807c16bcc2b6cd9cac95c05dd958e6b132deec53078fe088c51b830d28e1814fe98f70779c292b6401fbdae4c9f2612c99d5a143', 3, 'aktif', '2026-03-11 00:16:07', '/static/profile_photos/9fd92990e10941b499ce2c34766ed712.jpg'),
(18, 'avatar624', 'scrypt:32768:8:1$ah4wZcM6dBYooEmB$b7b60f064a7e2f724406ece27248b3b3d5401d7df79c58e6bd27ac3d73224db20ebbf2a7c9e30df1e5cc97bd41bbc688d25732fccf97710bcede0d5984f499a8', 2, 'aktif', '2026-03-14 15:10:22', NULL);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `detail_jawaban_kuisoner`
--
ALTER TABLE `detail_jawaban_kuisoner`
  ADD PRIMARY KEY (`id_detail_jawaban`),
  ADD KEY `fk_detail_jawaban` (`id_jawaban`),
  ADD KEY `fk_detail_pertanyaan` (`id_pertanyaan`);

--
-- Indeks untuk tabel `guru`
--
ALTER TABLE `guru`
  ADD PRIMARY KEY (`id_guru`),
  ADD UNIQUE KEY `uq_guru_nip` (`nip`),
  ADD KEY `idx_guru_user` (`id_user`);

--
-- Indeks untuk tabel `guru_mapel`
--
ALTER TABLE `guru_mapel`
  ADD PRIMARY KEY (`id_guru`,`id_mapel`),
  ADD KEY `idx_gm_mapel` (`id_mapel`);

--
-- Indeks untuk tabel `jadwal`
--
ALTER TABLE `jadwal`
  ADD PRIMARY KEY (`id_jadwal`),
  ADD KEY `idx_jadwal_kelas` (`id_kelas`),
  ADD KEY `idx_jadwal_mapel` (`id_mapel`);

--
-- Indeks untuk tabel `jadwal_guru`
--
ALTER TABLE `jadwal_guru`
  ADD PRIMARY KEY (`id_jadwal_guru`),
  ADD KEY `idx_jg_jadwal` (`id_jadwal`),
  ADD KEY `idx_jg_guru` (`id_guru`);

--
-- Indeks untuk tabel `jadwal_murid`
--
ALTER TABLE `jadwal_murid`
  ADD PRIMARY KEY (`id_jadwal`,`id_murid`),
  ADD KEY `idx_jm_murid` (`id_murid`);

--
-- Indeks untuk tabel `jawaban_kuisoner`
--
ALTER TABLE `jawaban_kuisoner`
  ADD PRIMARY KEY (`id_jawaban`),
  ADD UNIQUE KEY `unik_murid_isi_kuisoner` (`id_kuisoner`,`id_murid`),
  ADD KEY `fk_jawaban_murid` (`id_murid`);

--
-- Indeks untuk tabel `kehadiran_guru`
--
ALTER TABLE `kehadiran_guru`
  ADD PRIMARY KEY (`id_kehadiran`),
  ADD KEY `idx_kguru_guru` (`id_guru`);

--
-- Indeks untuk tabel `kehadiran_murid`
--
ALTER TABLE `kehadiran_murid`
  ADD PRIMARY KEY (`id_kehadiran`),
  ADD KEY `idx_kmurid_murid` (`id_murid`),
  ADD KEY `idx_kmurid_jadwal` (`id_jadwal`);

--
-- Indeks untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD PRIMARY KEY (`id_kelas`),
  ADD KEY `idx_kelas_tingkat` (`id_tingkat`);

--
-- Indeks untuk tabel `kelas_guru`
--
ALTER TABLE `kelas_guru`
  ADD PRIMARY KEY (`id_kelas`,`id_guru`),
  ADD KEY `idx_kg_guru` (`id_guru`);

--
-- Indeks untuk tabel `kelas_mapel`
--
ALTER TABLE `kelas_mapel`
  ADD PRIMARY KEY (`id_kelas`,`id_mapel`),
  ADD KEY `idx_km_mapel` (`id_mapel`);

--
-- Indeks untuk tabel `kuisoner`
--
ALTER TABLE `kuisoner`
  ADD PRIMARY KEY (`id_kuisoner`),
  ADD KEY `fk_kuisoner_jadwal` (`id_jadwal`);

--
-- Indeks untuk tabel `laporan_mengajar`
--
ALTER TABLE `laporan_mengajar`
  ADD PRIMARY KEY (`id_laporan`),
  ADD KEY `idx_lpm_id_monitor` (`id_monitor`);

--
-- Indeks untuk tabel `laporan_monitoring`
--
ALTER TABLE `laporan_monitoring`
  ADD PRIMARY KEY (`id_monitor`),
  ADD KEY `idx_lm_jadwal` (`id_jadwal`);

--
-- Indeks untuk tabel `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  ADD PRIMARY KEY (`id_log`),
  ADD KEY `idx_log_user` (`id_user`);

--
-- Indeks untuk tabel `mata_pelajaran`
--
ALTER TABLE `mata_pelajaran`
  ADD PRIMARY KEY (`id_mapel`),
  ADD KEY `idx_mapel_tingkat` (`id_tingkat`);

--
-- Indeks untuk tabel `murid`
--
ALTER TABLE `murid`
  ADD PRIMARY KEY (`id_murid`),
  ADD UNIQUE KEY `uq_murid_nis` (`nis`),
  ADD KEY `idx_murid_kelas` (`id_kelas`),
  ADD KEY `idx_murid_user` (`id_user`);

--
-- Indeks untuk tabel `murid_mapel`
--
ALTER TABLE `murid_mapel`
  ADD PRIMARY KEY (`id_murid_mapel`),
  ADD KEY `idx_mm_murid` (`id_murid`),
  ADD KEY `idx_mm_mapel` (`id_mapel`);

--
-- Indeks untuk tabel `murid_tingkat`
--
ALTER TABLE `murid_tingkat`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_mt_murid` (`id_murid`),
  ADD KEY `idx_mt_tingkat` (`id_tingkat`),
  ADD KEY `idx_mt_kelas` (`id_kelas`);

--
-- Indeks untuk tabel `nilai`
--
ALTER TABLE `nilai`
  ADD PRIMARY KEY (`id_nilai`),
  ADD KEY `idx_nilai_murid` (`id_murid`),
  ADD KEY `idx_nilai_jadwal` (`id_jadwal`);

--
-- Indeks untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  ADD PRIMARY KEY (`id_ortu`),
  ADD KEY `idx_ortu_murid` (`id_murid`),
  ADD KEY `idx_ortu_user` (`id_user`);

--
-- Indeks untuk tabel `pengaduan`
--
ALTER TABLE `pengaduan`
  ADD PRIMARY KEY (`id_pengaduan`),
  ADD KEY `fk_pengaduan_murid` (`id_murid`);

--
-- Indeks untuk tabel `penilaian_guru`
--
ALTER TABLE `penilaian_guru`
  ADD PRIMARY KEY (`id_penilaian`),
  ADD KEY `idx_pg_guru` (`id_guru`),
  ADD KEY `idx_pg_murid` (`id_murid`);

--
-- Indeks untuk tabel `pertanyaan_kuisoner`
--
ALTER TABLE `pertanyaan_kuisoner`
  ADD PRIMARY KEY (`id_pertanyaan`);

--
-- Indeks untuk tabel `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_role`),
  ADD UNIQUE KEY `uq_roles_nama_role` (`nama_role`);

--
-- Indeks untuk tabel `tingkat`
--
ALTER TABLE `tingkat`
  ADD PRIMARY KEY (`id_tingkat`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `uq_users_username` (`username`),
  ADD KEY `idx_users_role` (`id_role`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `detail_jawaban_kuisoner`
--
ALTER TABLE `detail_jawaban_kuisoner`
  MODIFY `id_detail_jawaban` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT untuk tabel `guru`
--
ALTER TABLE `guru`
  MODIFY `id_guru` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT untuk tabel `jadwal`
--
ALTER TABLE `jadwal`
  MODIFY `id_jadwal` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT untuk tabel `jadwal_guru`
--
ALTER TABLE `jadwal_guru`
  MODIFY `id_jadwal_guru` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `jawaban_kuisoner`
--
ALTER TABLE `jawaban_kuisoner`
  MODIFY `id_jawaban` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `kehadiran_guru`
--
ALTER TABLE `kehadiran_guru`
  MODIFY `id_kehadiran` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `kehadiran_murid`
--
ALTER TABLE `kehadiran_murid`
  MODIFY `id_kehadiran` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT untuk tabel `kelas`
--
ALTER TABLE `kelas`
  MODIFY `id_kelas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT untuk tabel `kuisoner`
--
ALTER TABLE `kuisoner`
  MODIFY `id_kuisoner` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT untuk tabel `laporan_mengajar`
--
ALTER TABLE `laporan_mengajar`
  MODIFY `id_laporan` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `laporan_monitoring`
--
ALTER TABLE `laporan_monitoring`
  MODIFY `id_monitor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT untuk tabel `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  MODIFY `id_log` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `mata_pelajaran`
--
ALTER TABLE `mata_pelajaran`
  MODIFY `id_mapel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `murid`
--
ALTER TABLE `murid`
  MODIFY `id_murid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `murid_mapel`
--
ALTER TABLE `murid_mapel`
  MODIFY `id_murid_mapel` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT untuk tabel `murid_tingkat`
--
ALTER TABLE `murid_tingkat`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT untuk tabel `nilai`
--
ALTER TABLE `nilai`
  MODIFY `id_nilai` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  MODIFY `id_ortu` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `pengaduan`
--
ALTER TABLE `pengaduan`
  MODIFY `id_pengaduan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `penilaian_guru`
--
ALTER TABLE `penilaian_guru`
  MODIFY `id_penilaian` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `pertanyaan_kuisoner`
--
ALTER TABLE `pertanyaan_kuisoner`
  MODIFY `id_pertanyaan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `roles`
--
ALTER TABLE `roles`
  MODIFY `id_role` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `tingkat`
--
ALTER TABLE `tingkat`
  MODIFY `id_tingkat` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `detail_jawaban_kuisoner`
--
ALTER TABLE `detail_jawaban_kuisoner`
  ADD CONSTRAINT `fk_detail_jawaban` FOREIGN KEY (`id_jawaban`) REFERENCES `jawaban_kuisoner` (`id_jawaban`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_detail_pertanyaan` FOREIGN KEY (`id_pertanyaan`) REFERENCES `pertanyaan_kuisoner` (`id_pertanyaan`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `guru`
--
ALTER TABLE `guru`
  ADD CONSTRAINT `fk_guru_user` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `guru_mapel`
--
ALTER TABLE `guru_mapel`
  ADD CONSTRAINT `fk_gm_guru` FOREIGN KEY (`id_guru`) REFERENCES `guru` (`id_guru`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_gm_mapel` FOREIGN KEY (`id_mapel`) REFERENCES `mata_pelajaran` (`id_mapel`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `jadwal`
--
ALTER TABLE `jadwal`
  ADD CONSTRAINT `fk_jadwal_kelas` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_jadwal_mapel` FOREIGN KEY (`id_mapel`) REFERENCES `mata_pelajaran` (`id_mapel`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `jadwal_guru`
--
ALTER TABLE `jadwal_guru`
  ADD CONSTRAINT `fk_jg_guru` FOREIGN KEY (`id_guru`) REFERENCES `guru` (`id_guru`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_jg_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `jadwal_murid`
--
ALTER TABLE `jadwal_murid`
  ADD CONSTRAINT `fk_jm_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_jm_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `jawaban_kuisoner`
--
ALTER TABLE `jawaban_kuisoner`
  ADD CONSTRAINT `fk_jawaban_kuisoner` FOREIGN KEY (`id_kuisoner`) REFERENCES `kuisoner` (`id_kuisoner`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_jawaban_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kehadiran_guru`
--
ALTER TABLE `kehadiran_guru`
  ADD CONSTRAINT `fk_kehadiran_guru_guru` FOREIGN KEY (`id_guru`) REFERENCES `guru` (`id_guru`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kehadiran_murid`
--
ALTER TABLE `kehadiran_murid`
  ADD CONSTRAINT `fk_kmurid_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_kmurid_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kelas`
--
ALTER TABLE `kelas`
  ADD CONSTRAINT `fk_kelas_tingkat` FOREIGN KEY (`id_tingkat`) REFERENCES `tingkat` (`id_tingkat`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kelas_guru`
--
ALTER TABLE `kelas_guru`
  ADD CONSTRAINT `fk_kg_guru` FOREIGN KEY (`id_guru`) REFERENCES `guru` (`id_guru`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_kg_kelas` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kelas_mapel`
--
ALTER TABLE `kelas_mapel`
  ADD CONSTRAINT `fk_km_kelas` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_km_mapel` FOREIGN KEY (`id_mapel`) REFERENCES `mata_pelajaran` (`id_mapel`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `kuisoner`
--
ALTER TABLE `kuisoner`
  ADD CONSTRAINT `fk_kuisoner_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `laporan_mengajar`
--
ALTER TABLE `laporan_mengajar`
  ADD CONSTRAINT `fk_lpm_monitor` FOREIGN KEY (`id_monitor`) REFERENCES `laporan_monitoring` (`id_monitor`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `laporan_monitoring`
--
ALTER TABLE `laporan_monitoring`
  ADD CONSTRAINT `fk_lm_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `log_aktivitas`
--
ALTER TABLE `log_aktivitas`
  ADD CONSTRAINT `fk_log_user` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `mata_pelajaran`
--
ALTER TABLE `mata_pelajaran`
  ADD CONSTRAINT `fk_mapel_tingkat` FOREIGN KEY (`id_tingkat`) REFERENCES `tingkat` (`id_tingkat`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `murid`
--
ALTER TABLE `murid`
  ADD CONSTRAINT `fk_murid_kelas` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_murid_user` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `murid_mapel`
--
ALTER TABLE `murid_mapel`
  ADD CONSTRAINT `fk_mm_mapel` FOREIGN KEY (`id_mapel`) REFERENCES `mata_pelajaran` (`id_mapel`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_mm_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `murid_tingkat`
--
ALTER TABLE `murid_tingkat`
  ADD CONSTRAINT `fk_mt_kelas` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_mt_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_mt_tingkat` FOREIGN KEY (`id_tingkat`) REFERENCES `tingkat` (`id_tingkat`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `nilai`
--
ALTER TABLE `nilai`
  ADD CONSTRAINT `fk_nilai_jadwal` FOREIGN KEY (`id_jadwal`) REFERENCES `jadwal` (`id_jadwal`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_nilai_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `orang_tua`
--
ALTER TABLE `orang_tua`
  ADD CONSTRAINT `fk_ortu_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_ortu_user` FOREIGN KEY (`id_user`) REFERENCES `users` (`id_user`) ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `pengaduan`
--
ALTER TABLE `pengaduan`
  ADD CONSTRAINT `fk_pengaduan_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `penilaian_guru`
--
ALTER TABLE `penilaian_guru`
  ADD CONSTRAINT `fk_pg_guru` FOREIGN KEY (`id_guru`) REFERENCES `guru` (`id_guru`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_pg_murid` FOREIGN KEY (`id_murid`) REFERENCES `murid` (`id_murid`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Ketidakleluasaan untuk tabel `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_users_role` FOREIGN KEY (`id_role`) REFERENCES `roles` (`id_role`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1
-- Dumped by pg_dump version 14.12 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: deleted_conversations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.deleted_conversations (
    id integer NOT NULL,
    user_id integer,
    job_id integer,
    other_user_id integer,
    deleted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: deleted_conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.deleted_conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: deleted_conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.deleted_conversations_id_seq OWNED BY public.deleted_conversations.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    urgent boolean DEFAULT false NOT NULL,
    date_posted timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer,
    locationn character varying(255) NOT NULL,
    exact_date date NOT NULL,
    start_time time without time zone NOT NULL,
    end_time time without time zone NOT NULL,
    contact_number character varying(20) NOT NULL,
    price numeric(10,2)
);


--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    sender_id integer,
    receiver_id integer,
    message text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    job_id integer NOT NULL
);


--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password character varying(200) NOT NULL,
    phone_number character varying(20),
    email character varying(255) NOT NULL,
    reset_token character varying(255),
    reset_expiration timestamp without time zone
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: deleted_conversations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations ALTER COLUMN id SET DEFAULT nextval('public.deleted_conversations_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: deleted_conversations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.deleted_conversations (id, user_id, job_id, other_user_id, deleted_at) FROM stdin;
1	5	8	5	2024-12-07 18:36:33.175328
2	5	11	8	2024-12-07 18:37:57.938037
3	8	16	4	2024-12-07 20:18:14.19473
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (id, title, description, urgent, date_posted, user_id, locationn, exact_date, start_time, end_time, contact_number, price) FROM stdin;
8	Cuidador de niños	niños buena onda	t	2024-10-05 23:37:56.314115	4	Plaza Antofagasta	2024-10-12	10:10:00	12:00:00	+56986323803	\N
9	programador	Buen programador con flask	f	2024-10-05 23:52:14.514536	4	Arica	2024-10-18	13:00:00	15:00:00	987434803	\N
10	Cuidador de gatos	sacar a pasear a mis gatos durante el día	t	2024-12-02 17:47:52.821019	5	Plaza Colon	2024-12-06	16:30:00	17:30:00	986342674	\N
11	Limpieza de depa	Limpiar las mesas y barrer el piso	t	2024-12-02 21:01:46.083765	5	Galleguillos Lorca 133	2024-12-05	15:00:00	16:00:00	989384764	\N
13	Programador Junior	Un programador que desarrolle en python	t	2024-12-03 11:46:39.558772	4	Plaza Antofagasta	2024-12-12	09:00:00	12:00:00	98349843	\N
14	Diseñador Grafico	Diseñar para restaurantes 	t	2024-12-03 13:11:32.70561	10	Antofgasta	2024-12-17	09:00:00	13:00:00	983746533	15000.00
15	Tareas de matemáticas	ejercicios de algebra para resolver	t	2024-12-03 19:17:27.254372	10	Santiago	2024-12-11	20:00:00	21:30:00	878378382	10000.00
16	Cuidar un cuaderno en sala	Vas a tener que estar por 1 hora cuidando que nadie se robe el cuaderno de la sala	t	2024-12-07 15:44:40.806016	8	antofagasta	2024-12-09	15:44:00	16:44:00	989384764	15000.00
17	Responder comentarios en redes sociales 	Solo duranto 4 horas responder onlinemente comentarios en redes sociales.	t	2024-12-07 16:05:35.045694	4	Trabajo Online	2024-12-11	09:00:00	12:00:00	989484885	40000.00
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.messages (id, sender_id, receiver_id, message, "timestamp", job_id) FROM stdin;
1	5	4	Hola amigo necesitas aún el cuidador?	2024-12-02 17:49:09.119477	8
2	4	5	Hola amigo, sí necesito para este viernes un cuidador 	2024-12-02 20:08:56.178799	8
3	5	4	Okey, yo mismo soy pero dejame tu número de celular. 	2024-12-02 20:10:19.986829	8
4	7	5	Hola Benja, quiero cuidar a esos gatitos traviesos, todavía sera posible?	2024-12-02 20:20:38.714302	8
5	5	7	Hola Pedro, como va, lamento decirte que ya no podré.	2024-12-02 20:21:40.165777	8
6	5	5	Hola amigo	2024-12-02 20:58:46.125303	8
7	5	5	como estas	2024-12-02 21:02:16.959806	8
8	4	5	hoal	2024-12-02 21:09:55.157791	8
9	5	5	Como te va en todo	2024-12-02 21:10:15.814078	8
10	5	4	como te va en todo	2024-12-02 21:11:19.970892	8
11	4	5	aqui bien amigo	2024-12-02 21:11:35.231448	8
12	5	4	y a ti como te va 	2024-12-02 21:11:48.916981	8
13	5	4	como es esto	2024-12-02 21:15:00.864564	8
14	4	4	hay algun problema 	2024-12-02 21:15:16.827964	8
15	4	5	buen	2024-12-02 21:40:46.418708	8
16	5	4	como asi	2024-12-02 21:40:56.30154	8
17	4	5	vamos 	2024-12-02 21:41:58.330507	8
18	5	4	vamos que si 	2024-12-02 21:42:09.915276	8
19	5	4	de cuanto estamos hablando?	2024-12-02 21:47:07.896518	8
20	4	5	sabes algo de programación?	2024-12-02 21:52:50.174225	8
21	5	4	no se nada de programación\r\n	2024-12-02 21:53:15.564613	8
22	5	4	vamos con todo	2024-12-02 21:53:44.052879	8
23	5	4	adivina que 	2024-12-03 01:00:00	8
24	5	4	hola amigos	2024-12-03 01:00:00	8
25	5	4	vamos	2024-12-03 01:01:00	8
26	4	5	pero que es lo que tu quieres mi bro	2024-12-03 01:06:00	8
27	4	5	vamos con todo amigo	2024-12-03 01:07:00	8
28	5	4	no creo que todo vaya mejor	2024-12-03 01:07:00	8
29	5	4	como vamos	2024-12-03 01:10:00	8
30	5	4	vamos bien	2024-12-03 01:21:00	8
31	5	4	que dices ahora	2024-12-03 01:23:00	8
32	5	4	hola como vas	2024-12-03 01:30:00	8
33	5	4	que onda mi bro	2024-12-03 01:33:00	8
34	5	4	a donde vamos ahora?	2024-12-03 01:33:00	8
35	4	5	hola de nuevo	2024-12-03 01:38:00	8
36	4	5	hola	2024-12-03 01:41:00	8
37	4	5	hola	2024-12-03 01:42:00	8
38	5	4	hu	2024-12-03 01:49:00	8
39	4	8	Hoa 	2024-12-03 00:44:48.556705	8
40	8	4	hola mi bro	2024-12-03 00:45:15.311059	8
41	4	8	como estas	2024-12-03 00:45:21.677698	8
42	4	8	haces algo mas o no ?	2024-12-03 00:45:33.8449	8
43	8	4	vamos con todo	2024-12-03 00:45:42.675796	8
44	4	8	hola amigos	2024-12-03 03:49:00	8
45	4	8	como vamos	2024-12-03 03:50:00	8
46	8	4	necesitas algo mas ?	2024-12-03 03:52:00	8
47	8	4	vamos	2024-12-03 03:57:00	8
48	8	5	hola benja	2024-12-03 01:05:16.791151	8
49	4	8	vamos con todo	2024-12-03 04:09:00	8
50	8	4	hola amigo emerson	2024-12-03 04:13:00	8
51	5	4	volviendo por aqui	2024-12-03 15:41:00	8
52	5	8	hola nuevamente	2024-12-03 16:02:00	8
53	5	8	Que novedades	2024-12-03 16:02:00	8
54	5	4	Hola programador Junior	2024-12-03 16:02:00	8
55	5	4	hola buen amigo	2024-12-03 16:04:00	8
56	5	8	Hola buen samaritano	2024-12-03 16:05:00	8
57	5	4	buen samaritano	2024-12-03 16:06:00	8
58	5	4	Ya estuve conversando contigo sobre esto	2024-12-03 16:07:00	8
59	10	5	Hola benja, quisiera cuidar sus gatitos	2024-12-03 16:12:00	8
60	10	5	Ahora tambien quisiera limpiar su depa 	2024-12-03 16:13:00	8
61	10	4	Hola emerson, me interesa cuidar niños.	2024-12-03 16:54:00	8
62	10	5	Necesito cuidar los gatos	2024-12-03 17:25:00	8
63	10	5	cuidar los gatos	2024-12-03 17:26:00	8
64	10	4	hola amigo	2024-12-03 17:26:00	8
65	10	4	vamos a cuidar los niños	2024-12-03 17:27:00	8
66	10	4	quiere algo mas 	2024-12-03 17:28:00	8
67	10	4	hola emerson	2024-12-03 17:48:00	9
68	10	4	como va todo con los proyectos?	2024-12-03 17:48:00	9
69	10	5	Hola, quisiera hacer limpieza de departamentos.	2024-12-03 17:55:00	11
70	10	5	Hola benja, quisiera cuidar gatitos, te parece para el viernes?	2024-12-03 17:56:00	10
71	5	10	Hola Alaska, quiero ser una diseñador grafico. 	2024-12-03 17:57:00	14
72	5	10	Necesito saber que día podemos coordinar	2024-12-03 18:01:00	14
73	10	5	Que novedades	2024-12-03 18:33:00	10
75	5	4	Quisiera ser un buen programador	2024-12-03 18:37:00	13
76	5	4	Hola emer, buscas programador?	2024-12-03 18:56:00	9
77	7	4	hola emerson,	2024-12-03 18:58:00	8
78	7	5	hola benja	2024-12-03 18:59:00	10
79	4	4	hola amigo, necesito trabajar solo 3 horas que dices?	2024-12-03 20:55:00	8
80	4	5	Hola amigo, como te en todo	2024-12-03 20:56:00	11
82	11	4	Hola Emerson, necesito subir saber mas sobre el puesto a desarrollar	2024-12-04 00:42:00	13
83	5	10	necesito este trabajo	2024-12-04 00:51:00	15
87	8	4	como va todo	2024-12-07 16:40:00	8
90	4	8	Hola juanito como estas, necesito cuidar ese cuaderno.	2024-12-07 18:45:29.940873	16
91	8	4	hola amigo	2024-12-07 18:58:11.725256	16
92	4	8	hay alguna forma de hacer las cosas correctas	2024-12-07 18:58:45.881532	16
93	8	4	por su puesto	2024-12-07 19:01:55.44419	16
96	8	4	hey amirgo	2024-12-07 19:29:31.193408	16
97	8	4	Vamos con todo	2024-12-07 19:29:37.992409	16
99	8	4	holla	2024-12-07 19:34:04.880677	17
100	8	4	como va tood	2024-12-07 19:34:13.017801	17
102	4	8	vamos bien	2024-12-07 19:37:07.645638	17
103	4	8	y tu que tal como vas ?	2024-12-07 19:37:14.479496	17
104	8	4	Yo aquí bien tambine	2024-12-07 19:37:27.636996	17
105	8	10	Hola Alaska,  necesito hacer las cosas de mejor manera.	2024-12-07 19:40:12.146096	15
106	10	8	Hola Juanito, me parece que puedas seguir en esto	2024-12-07 19:40:38.399741	15
107	10	8	quisiera ser un gran conquistador	2024-12-07 19:40:59.250486	15
108	8	10	Estamos trabajando para conseguir los mejores trabajos	2024-12-07 19:41:16.030743	15
109	10	8	estamos bien ?	2024-12-07 19:45:46.986934	15
110	4	8	ahora si que anda bien	2024-12-07 19:47:19.260502	17
111	4	8	hey	2024-12-07 20:00:03.695376	16
112	4	8	como estas	2024-12-07 20:00:10.000367	16
113	4	8	hi	2024-12-07 20:00:47.264565	16
114	8	4	ahora si que vamos bien	2024-12-07 20:01:34.57759	16
118	8	5	Hola Benja, necesito esa peguita	2024-12-07 20:06:02.076391	11
119	5	8	Como estas, por supuesto que puede ser tuyo la pega	2024-12-07 20:06:24.931275	11
120	8	5	Buu	2024-12-07 21:19:08.757524	11
121	5	8	buuu	2024-12-07 21:20:26.866451	11
122	5	8	facebook	2024-12-07 21:20:33.661854	11
123	8	5	vamos con todo	2024-12-07 21:20:42.705443	11
124	5	8	con todo	2024-12-07 21:24:15.210572	11
125	8	5	hola juanito	2024-12-07 23:21:42.118063	11
126	8	5	hol	2024-12-07 23:21:48.665545	11
127	8	5	Hola benja	2024-12-07 23:22:49.162033	11
128	8	5	hola benja	2024-12-07 23:31:17.937138	11
129	5	7	Hola pedrito	2024-12-07 23:34:52.930678	10
130	7	5	como te va en todo	2024-12-07 23:35:34.77159	10
131	7	5	estamos preparandonos para navidad	2024-12-07 23:35:49.581348	10
132	5	7	como crees que nos ira ahora que ya esta mejorando las acciones de navidad	2024-12-07 23:36:08.620324	10
133	7	5	Como te va a ti,y que cosas interesantes sabes hacer	2024-12-08 00:08:26.423203	10
134	5	7	me va todo bien y hay muchas cosas intersante por ver	2024-12-08 00:08:45.531988	10
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password, phone_number, email, reset_token, reset_expiration) FROM stdin;
4	emerson	$2b$12$wa03VC9dqN18VUAXo4jZpep6NwlqOo1ad9FMxo8gcVqzx46eR8mpG	\N	xinayespinoza@gmail.com	\N	\N
7	pedro	$2b$12$0Nvq5apxxDTXdftxsXv0T.SrrYMWtw.c5YAXFctNon6T/0oOTtJVm	\N	pedro@gmail.com	\N	\N
10	alaska	$2b$12$B/A9FQ4RhOZbFAqcPc9Mc..IGZGhGXIlynr8Bz1obW/moXxXLN0KC	\N	alaska@gmail.com	\N	\N
5	benja	$2b$12$sSbNXoXH20QFF38CGolFcuqgaX7N3.IURGgVZqa.ZjBFbWgR2aQh2	987656876	benja@gmail.com	\N	\N
11	brandom	$2b$12$WbHyT.adIErafinWU/q1/OkPjlzXu0yF4JtSrlemTGBJDGxVYWkK6	\N	brandom@gmail.com	\N	\N
8	juanito	$2b$12$Hg.b1ultwWxolH6YCSbzYeF7Sl6/A6HCimA8Et.v/7CsE2Jpzm73i	980323803	juanito@gmail.com	\N	\N
\.


--
-- Name: deleted_conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.deleted_conversations_id_seq', 3, true);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.jobs_id_seq', 17, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.messages_id_seq', 134, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 11, true);


--
-- Name: deleted_conversations deleted_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations
    ADD CONSTRAINT deleted_conversations_pkey PRIMARY KEY (id);


--
-- Name: deleted_conversations deleted_conversations_user_id_job_id_other_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations
    ADD CONSTRAINT deleted_conversations_user_id_job_id_other_user_id_key UNIQUE (user_id, job_id, other_user_id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: users unique_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_email UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: deleted_conversations deleted_conversations_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations
    ADD CONSTRAINT deleted_conversations_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: deleted_conversations deleted_conversations_other_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations
    ADD CONSTRAINT deleted_conversations_other_user_id_fkey FOREIGN KEY (other_user_id) REFERENCES public.users(id);


--
-- Name: deleted_conversations deleted_conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.deleted_conversations
    ADD CONSTRAINT deleted_conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: messages fk_job_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_job_id FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: jobs jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: messages messages_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: messages messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


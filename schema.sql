--
-- PostgreSQL database dump
--

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

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
-- Name: prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prices (
    day date NOT NULL,
    hour integer NOT NULL,
    price real NOT NULL,
    is_cheap boolean NOT NULL
);


--
-- Name: readings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.readings (
    id integer NOT NULL,
    ts timestamp with time zone DEFAULT now() NOT NULL,
    humidity real NOT NULL,
    temperature real NOT NULL,
    plug_on boolean,
    price real,
    source text NOT NULL,
    device text,
    battery real,
    linkquality integer
);


--
-- Name: readings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.readings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: readings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.readings_id_seq OWNED BY public.readings.id;


--
-- Name: switches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.switches (
    id integer NOT NULL,
    ts timestamp with time zone DEFAULT now() NOT NULL,
    turned_on boolean NOT NULL,
    reason text,
    humidity real,
    price real
);


--
-- Name: switches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.switches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: switches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.switches_id_seq OWNED BY public.switches.id;


--
-- Name: readings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.readings ALTER COLUMN id SET DEFAULT nextval('public.readings_id_seq'::regclass);


--
-- Name: switches id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.switches ALTER COLUMN id SET DEFAULT nextval('public.switches_id_seq'::regclass);


--
-- Name: prices prices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT prices_pkey PRIMARY KEY (day, hour);


--
-- Name: readings readings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.readings
    ADD CONSTRAINT readings_pkey PRIMARY KEY (id);


--
-- Name: switches switches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.switches
    ADD CONSTRAINT switches_pkey PRIMARY KEY (id);


--
-- Name: idx_readings_src_ts; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_readings_src_ts ON public.readings USING btree (source, ts DESC);


--
-- Name: readings_ts_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX readings_ts_idx ON public.readings USING btree (ts DESC);


--
-- PostgreSQL database dump complete
--

\unrestrict ioeweepcas5cxMhemXRW3SgkklZSeWl2O26V4ggA5L1mprlgJVaq1wsEkSoIa9N


--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 12.1

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


CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


CREATE TABLE public.chapter (
    id integer NOT NULL,
    title character varying(128) NOT NULL,
    summary character varying(1024) DEFAULT ''::character varying NOT NULL,
    note text,
    status character varying(128) DEFAULT '写作中'::character varying NOT NULL,
    word_count integer DEFAULT 0 NOT NULL,
    dest_word_count integer DEFAULT '-1'::integer NOT NULL,
    ctime timestamp without time zone,
    utime timestamp without time zone,
    parent integer,
    order_id integer,
    library_id integer,
    chapter_type character varying(128) DEFAULT 'chapter'::character varying NOT NULL,
    context text,
    cover character varying(128),
    update_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.chapter OWNER TO app;

--
-- Name: chapter_id_seq; Type: SEQUENCE; Schema: public; Owner: app
--

CREATE SEQUENCE public.chapter_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chapter_id_seq OWNER TO app;

--
-- Name: chapter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: app
--

ALTER SEQUENCE public.chapter_id_seq OWNED BY public.chapter.id;


--
-- Name: ffmpeg_info; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.ffmpeg_info (
    pid integer,
    command text
);


ALTER TABLE public.ffmpeg_info OWNER TO app;

--
-- Name: item; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.item (
    id integer NOT NULL,
    name text,
    cover integer,
    path text,
    parent integer,
    library_id integer,
    version integer,
    order_id integer DEFAULT '-1'::integer NOT NULL,
    item_type character varying(128) DEFAULT 'file'::character varying NOT NULL,
    ctime timestamp without time zone,
    utime timestamp without time zone,
    file_type character varying(128) DEFAULT 'file'::character varying NOT NULL
);


ALTER TABLE public.item OWNER TO app;

--
-- Name: item_id_seq; Type: SEQUENCE; Schema: public; Owner: app
--

CREATE SEQUENCE public.item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_id_seq OWNER TO app;

--
-- Name: item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: app
--

ALTER SEQUENCE public.item_id_seq OWNED BY public.item.id;


--
-- Name: lib_user; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.lib_user (
    username character varying(128),
    passwd character varying(128)
);


ALTER TABLE public.lib_user OWNER TO app;

--
-- Name: library; Type: TABLE; Schema: public; Owner: app
--

CREATE TABLE public.library (
    id integer NOT NULL,
    name character varying(128) NOT NULL,
    dir character varying(1024),
    status character varying(16),
    version integer,
    lib_type character varying(1024) DEFAULT 'photo'::character varying NOT NULL,
    skip_dir character varying(1024) DEFAULT ''::character varying NOT NULL,
    skip_file character varying(1024) DEFAULT ''::character varying NOT NULL,
    support_file character varying(1024) DEFAULT ''::character varying NOT NULL,
    CONSTRAINT library_status_check CHECK (((status)::text = ANY (ARRAY[('syncing'::character varying)::text, ('synced'::character varying)::text, ('unsync'::character varying)::text])))
);


ALTER TABLE public.library OWNER TO app;

--
-- Name: library_id_seq; Type: SEQUENCE; Schema: public; Owner: app
--

CREATE SEQUENCE public.library_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.library_id_seq OWNER TO app;

--
-- Name: library_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: app
--

ALTER SEQUENCE public.library_id_seq OWNED BY public.library.id;


--
-- Name: chapter id; Type: DEFAULT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.chapter ALTER COLUMN id SET DEFAULT nextval('public.chapter_id_seq'::regclass);


--
-- Name: item id; Type: DEFAULT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.item ALTER COLUMN id SET DEFAULT nextval('public.item_id_seq'::regclass);


--
-- Name: library id; Type: DEFAULT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.library ALTER COLUMN id SET DEFAULT nextval('public.library_id_seq'::regclass);


--
-- Name: chapter chapter_pkey; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.chapter
    ADD CONSTRAINT chapter_pkey PRIMARY KEY (id);


--
-- Name: item item_pkey; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_pkey PRIMARY KEY (id);


--
-- Name: library library_pkey; Type: CONSTRAINT; Schema: public; Owner: app
--

ALTER TABLE ONLY public.library
    ADD CONSTRAINT library_pkey PRIMARY KEY (id);


--
-- Name: idx_chapter; Type: INDEX; Schema: public; Owner: app
--

CREATE INDEX idx_chapter ON public.chapter USING btree (library_id, id);


--
-- Name: idx_item_parent_order_id; Type: INDEX; Schema: public; Owner: app
--

CREATE INDEX idx_item_parent_order_id ON public.item USING btree (parent, order_id);


--
-- Name: idx_itwm_name; Type: INDEX; Schema: public; Owner: app
--

CREATE INDEX idx_itwm_name ON public.item USING gin (name public.gin_trgm_ops);


--
-- Name: idx_libid_item_id; Type: INDEX; Schema: public; Owner: app
--

CREATE INDEX idx_libid_item_id ON public.item USING btree (library_id, id);


--
-- Name: unq_item_path; Type: INDEX; Schema: public; Owner: app
--

CREATE UNIQUE INDEX unq_item_path ON public.item USING btree (library_id, path);


--
-- Name: unq_library_name; Type: INDEX; Schema: public; Owner: app
--

CREATE UNIQUE INDEX unq_library_name ON public.library USING btree (name);


--
-- Name: unq_user; Type: INDEX; Schema: public; Owner: app
--

CREATE UNIQUE INDEX unq_user ON public.lib_user USING btree (username);


--
-- PostgreSQL database dump complete
--


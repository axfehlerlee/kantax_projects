-- TEST FIXTURE ONLY. Used inside a random isolated schema by test_postgresql.py.
-- No rows or credentials. Do not apply this to an existing application DB.
--
-- PostgreSQL database dump
--


-- Dumped from database version 17.11 (Debian 17.11-1.pgdg13+2)
-- Dumped by pg_dump version 17.11 (Debian 17.11-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: boards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.boards (
    id character varying(40) NOT NULL,
    board_name character varying(65) NOT NULL,
    edit_role character varying(30) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone NOT NULL,
    modified_at timestamp with time zone,
    deleted_at timestamp with time zone,
    page_size integer DEFAULT 20 NOT NULL,
    view_role character varying(20) DEFAULT 'ALL'::character varying NOT NULL,
    list_role character varying(20) DEFAULT 'ALL'::character varying NOT NULL,
    comment_list_role character varying(20) DEFAULT 'ALL'::character varying NOT NULL,
    comment_edit_role character varying(20) DEFAULT 'ALL'::character varying NOT NULL
);


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    id bigint NOT NULL,
    post_id bigint NOT NULL,
    content text NOT NULL,
    author_name character varying(50) NOT NULL,
    author_id uuid,
    guest_password character varying(65),
    created_at timestamp with time zone NOT NULL,
    modified_at timestamp with time zone,
    deleted_at timestamp with time zone
);


--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posts (
    id bigint NOT NULL,
    category character varying(60),
    title character varying(255) NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    modified_at timestamp with time zone,
    deleted_at timestamp with time zone,
    board_id character varying(40) NOT NULL,
    author_name character varying(50) DEFAULT '익명'::character varying NOT NULL,
    author_id uuid,
    guest_password character varying(65)
);


--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: token_blacklist; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.token_blacklist (
    jti character varying(36) NOT NULL,
    expired_at timestamp with time zone NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    name character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    resign boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    modified_at timestamp with time zone,
    deleted_at timestamp with time zone
);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: boards boards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.boards
    ADD CONSTRAINT boards_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: token_blacklist token_blacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.token_blacklist
    ADD CONSTRAINT token_blacklist_pkey PRIMARY KEY (jti);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_comments_post_id_deleted_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_comments_post_id_deleted_at ON public.comments USING btree (post_id, deleted_at);


--
-- Name: ix_posts_board_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_posts_board_id ON public.posts USING btree (board_id);


--
-- Name: ix_posts_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_posts_category ON public.posts USING btree (category);


--
-- Name: ix_token_blacklist_expired_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_token_blacklist_expired_at ON public.token_blacklist USING btree (expired_at);


--
-- Name: ix_token_blacklist_jti; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_token_blacklist_jti ON public.token_blacklist USING btree (jti);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: comments comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: comments comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: posts posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: posts posts_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_board_id_fkey FOREIGN KEY (board_id) REFERENCES public.boards(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--



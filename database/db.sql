--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

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
-- Name: contact; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact (
    id character varying(255) NOT NULL,
    location_id character varying(255),
    first_name character varying(255),
    last_name character varying(255),
    email character varying(255),
    company_name character varying(255),
    phone character varying(50),
    assigned_to character varying(255),
    address1 text,
    city character varying(255),
    state character varying(255),
    country character varying(255),
    postal_code character varying(50),
    website character varying(255),
    date_of_birth date
);


ALTER TABLE public.contact OWNER TO postgres;

--
-- Name: contact_custom_fields; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contact_custom_fields (
    id integer NOT NULL,
    custom_field_value character varying(255),
    contact_id character varying,
    custom_field_id character varying,
    value text
);


ALTER TABLE public.contact_custom_fields OWNER TO postgres;

--
-- Name: contact_custom_fields_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contact_custom_fields_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_custom_fields_id_seq OWNER TO postgres;

--
-- Name: contact_custom_fields_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contact_custom_fields_id_seq OWNED BY public.contact_custom_fields.id;


--
-- Name: custom_fields; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.custom_fields (
    id character varying NOT NULL,
    name character varying,
    field_key character varying,
    placeholder character varying,
    "position" integer,
    datatype character varying,
    picklist_options text
);


ALTER TABLE public.custom_fields OWNER TO postgres;

--
-- Name: location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.location (
    id character varying(255) NOT NULL,
    company_id character varying(255),
    name character varying(255),
    domain character varying(255),
    address text,
    city character varying(255),
    state character varying(255),
    country character varying(255),
    postal_code character varying(50),
    website character varying(255),
    timezone character varying(50),
    first_name character varying(255),
    last_name character varying(255),
    email character varying(255),
    phone character varying(50),
    logo_url character varying(255)
);


ALTER TABLE public.location OWNER TO postgres;

--
-- Name: realtorfridayupdates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.realtorfridayupdates (
    id integer NOT NULL,
    contact_realtor_email character varying(255) NOT NULL,
    contact_name character varying(255) NOT NULL,
    contact_address text NOT NULL,
    contact_phone character varying(20) NOT NULL
);


ALTER TABLE public.realtorfridayupdates OWNER TO postgres;

--
-- Name: realtorfridayupdates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.realtorfridayupdates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.realtorfridayupdates_id_seq OWNER TO postgres;

--
-- Name: realtorfridayupdates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.realtorfridayupdates_id_seq OWNED BY public.realtorfridayupdates.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    location_id character varying(255),
    first_name character varying(255),
    last_name character varying(255),
    email character varying(255),
    phone character varying(50),
    role_type character varying(50),
    role character varying(50),
    twilio_phone character varying(50)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: contact_custom_fields id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_custom_fields ALTER COLUMN id SET DEFAULT nextval('public.contact_custom_fields_id_seq'::regclass);


--
-- Name: realtorfridayupdates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.realtorfridayupdates ALTER COLUMN id SET DEFAULT nextval('public.realtorfridayupdates_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: contact_custom_fields contact_custom_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_custom_fields
    ADD CONSTRAINT contact_custom_fields_pkey PRIMARY KEY (id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- Name: custom_fields custom_fields_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.custom_fields
    ADD CONSTRAINT custom_fields_pkey PRIMARY KEY (id);


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (id);


--
-- Name: realtorfridayupdates realtorfridayupdates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.realtorfridayupdates
    ADD CONSTRAINT realtorfridayupdates_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: custom_fields_id_unique; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX custom_fields_id_unique ON public.custom_fields USING btree (id);


--
-- Name: idx_contact_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_email ON public.contact USING btree (email);


--
-- Name: idx_contact_first_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_first_name ON public.contact USING btree (first_name);


--
-- Name: idx_contact_last_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_last_name ON public.contact USING btree (last_name);


--
-- Name: idx_contact_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_contact_location ON public.contact USING btree (location_id);


--
-- Name: idx_location_first_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_location_first_name ON public.location USING btree (first_name);


--
-- Name: idx_location_last_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_location_last_name ON public.location USING btree (last_name);


--
-- Name: idx_user_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_email ON public.users USING btree (email);


--
-- Name: idx_user_first_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_first_name ON public.users USING btree (first_name);


--
-- Name: idx_user_last_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_last_name ON public.users USING btree (last_name);


--
-- Name: idx_user_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_location ON public.users USING btree (location_id);


--
-- Name: contact_custom_fields contact_custom_fields_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_custom_fields
    ADD CONSTRAINT contact_custom_fields_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contact(id) ON DELETE CASCADE;


--
-- Name: contact_custom_fields contact_custom_fields_custom_field_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact_custom_fields
    ADD CONSTRAINT contact_custom_fields_custom_field_id_fkey FOREIGN KEY (custom_field_id) REFERENCES public.custom_fields(id) ON DELETE CASCADE;


--
-- Name: contact contact_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(id);


--
-- Name: users users_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(id);


--
-- PostgreSQL database dump complete
--

